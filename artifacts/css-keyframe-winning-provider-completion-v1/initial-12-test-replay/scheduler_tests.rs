#[path = "winning_provider_completion.rs"]
mod scheduler;

use scheduler::{Evaluation, Failure, Provider, ProviderView, Winner, WinningProviders};
use std::collections::HashMap;

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct Key(u32);

#[derive(Clone, Debug, PartialEq)]
enum Token {
    Number(f64),
    WrongType,
    Invalid,
}

enum Recipe {
    Literal(Token),
    Alias(Key),
    Registered {
        provider: Key,
        fallback: Option<f64>,
        position: f64,
    },
    Fallback {
        provider: Key,
        fallback: Key,
    },
    Error,
    Demand(Key),
}

type Work = WinningProviders<f64, Key, Token, Recipe>;
type View<'a> = ProviderView<'a, Key, Token, Recipe>;
type Step = Evaluation<Key, Token, Vec<Key>, &'static str>;

fn mock_endpoint(initial: &f64, name: &Key, recipe: &Recipe, providers: &View<'_>) -> Step {
    let ready = |value| Evaluation::Complete {
        value,
        effects: vec![*name],
    };
    match recipe {
        Recipe::Literal(value) => ready(value.clone()),
        Recipe::Alias(key) => match providers.get(key) {
            Provider::Ready(value) => ready(value.clone()),
            Provider::Missing => ready(Token::Invalid),
            Provider::Pending => Evaluation::Need(*key),
        },
        Recipe::Registered {
            provider,
            fallback,
            position,
        } => {
            let start = match providers.get(provider) {
                Provider::Ready(Token::Number(value)) => *value,
                Provider::Ready(Token::WrongType) => *initial,
                Provider::Ready(Token::Invalid) | Provider::Missing => fallback.unwrap_or(*initial),
                Provider::Pending => return Evaluation::Need(*provider),
            };
            ready(Token::Number(start * (1.0 - position) + 30.0 * position))
        }
        Recipe::Fallback { provider, fallback } => match providers.get(provider) {
            Provider::Ready(value) if *value != Token::Invalid => ready(value.clone()),
            Provider::Pending => Evaluation::Need(*provider),
            _ => match providers.get(fallback) {
                Provider::Ready(value) => ready(value.clone()),
                Provider::Missing => ready(Token::Invalid),
                Provider::Pending => Evaluation::Need(*fallback),
            },
        },
        Recipe::Error => Evaluation::Error("evaluator failed"),
        Recipe::Demand(key) => Evaluation::Need(*key),
    }
}

fn add(work: &mut Work, key: u32, recipe: Recipe) {
    assert!(work.admit(Key(key), Winner::Pending(recipe)).is_ok());
}

fn finish(work: Work) -> (HashMap<Key, Token>, Vec<(Key, Vec<Key>)>) {
    match work.resolve_all(mock_endpoint) {
        Ok(result) => {
            let (_, values, effects) = result.into_parts();
            (values, effects)
        }
        Err(error) => panic!("unexpected failure: {:?}", error.reason()),
    }
}

#[test]
fn mock_dynamic_histories_request_current_pending_provider() {
    for reverse in [false, true] {
        for fallback in [None, Some(5.0)] {
            for provider in [Token::Number(20.0), Token::WrongType, Token::Number(20.0)] {
                for position in [0.0, 0.5, 1.0] {
                    let mut work = Work::new(10.0, HashMap::from([(Key(1), Token::Number(99.0))]));
                    let consumer = Recipe::Registered {
                        provider: Key(1),
                        fallback,
                        position,
                    };
                    if reverse {
                        add(&mut work, 2, consumer);
                        add(&mut work, 1, Recipe::Literal(provider.clone()));
                    } else {
                        add(&mut work, 1, Recipe::Literal(provider.clone()));
                        add(&mut work, 2, consumer);
                    }
                    let (values, _) = finish(work);
                    let start = if provider == Token::WrongType {
                        10.0
                    } else {
                        20.0
                    };
                    assert_eq!(
                        values[&Key(2)],
                        Token::Number(start * (1.0 - position) + 30.0 * position)
                    );
                }
            }
        }
    }
}

#[test]
fn acyclic_chain_completes_in_one_transaction_in_reverse_order() {
    let mut work = Work::new(
        10.0,
        HashMap::from([(Key(1), Token::Number(20.0)), (Key(2), Token::Number(20.0))]),
    );
    add(&mut work, 3, Recipe::Alias(Key(2)));
    add(&mut work, 2, Recipe::Alias(Key(1)));
    add(&mut work, 1, Recipe::Literal(Token::Number(40.0)));
    let (values, effects) = finish(work);
    assert_eq!(values[&Key(3)], Token::Number(40.0));
    assert_eq!(
        effects.iter().map(|(key, _)| *key).collect::<Vec<_>>(),
        [Key(1), Key(2), Key(3)]
    );
}

#[test]
fn missing_invalid_and_wrong_type_remain_distinct_mock_inputs() {
    for (base, expected) in [
        (None, 5.0),
        (Some(Token::Invalid), 5.0),
        (Some(Token::WrongType), 10.0),
    ] {
        let mut work = Work::new(
            10.0,
            base.into_iter().map(|value| (Key(1), value)).collect(),
        );
        add(
            &mut work,
            2,
            Recipe::Registered {
                provider: Key(1),
                fallback: Some(5.0),
                position: 0.0,
            },
        );
        assert_eq!(finish(work).0[&Key(2)], Token::Number(expected));
    }
}

#[test]
fn unused_fallback_is_not_a_dependency() {
    let mut work = Work::new(10.0, HashMap::new());
    add(
        &mut work,
        2,
        Recipe::Fallback {
            provider: Key(1),
            fallback: Key(2),
        },
    );
    add(&mut work, 1, Recipe::Literal(Token::Number(40.0)));
    assert_eq!(finish(work).0[&Key(2)], Token::Number(40.0));
}

#[test]
fn used_fallback_cycle_is_incomplete_not_invalid_or_initial() {
    let mut work = Work::new(10.0, HashMap::new());
    add(
        &mut work,
        2,
        Recipe::Fallback {
            provider: Key(1),
            fallback: Key(2),
        },
    );
    let Err(incomplete) = work.resolve_all(mock_endpoint) else {
        panic!("published a cycle")
    };
    assert_eq!(incomplete.reason(), &Failure::Cycle(vec![Key(2), Key(2)]));
    incomplete.discard();
}

#[test]
fn two_winner_cycle_retains_exact_path() {
    let mut work = Work::new(10.0, HashMap::from([(Key(1), Token::Number(7.0))]));
    add(&mut work, 1, Recipe::Alias(Key(2)));
    add(&mut work, 2, Recipe::Alias(Key(1)));
    let Err(incomplete) = work.resolve_all(mock_endpoint) else {
        panic!("published a cycle")
    };
    assert_eq!(
        incomplete.reason(),
        &Failure::Cycle(vec![Key(1), Key(2), Key(1)])
    );
}

#[test]
fn internal_error_does_not_become_missing_or_use_fallback() {
    let mut work = Work::new(10.0, HashMap::new());
    add(
        &mut work,
        2,
        Recipe::Registered {
            provider: Key(1),
            fallback: Some(5.0),
            position: 0.0,
        },
    );
    add(&mut work, 1, Recipe::Error);
    let Err(incomplete) = work.resolve_all(mock_endpoint) else {
        panic!("defaulted an error")
    };
    assert_eq!(
        incomplete.reason(),
        &Failure::Endpoint {
            property: Key(1),
            error: "evaluator failed"
        }
    );
}

#[test]
fn duplicate_winner_refused_without_replacing_ready_winner() {
    let mut work = Work::new(10.0, HashMap::new());
    assert!(
        work.admit(Key(1), Winner::Ready(Token::Number(40.0)))
            .is_ok()
    );
    assert!(work.admit(Key(1), Winner::Pending(Recipe::Error)).is_err());
    add(&mut work, 2, Recipe::Alias(Key(1)));
    assert_eq!(finish(work).0[&Key(2)], Token::Number(40.0));
}

#[test]
fn ready_or_missing_demand_is_rejected_instead_of_spinning() {
    for base in [
        HashMap::new(),
        HashMap::from([(Key(1), Token::Number(40.0))]),
    ] {
        let mut work = Work::new(10.0, base);
        add(&mut work, 2, Recipe::Demand(Key(1)));
        let Err(incomplete) = work.resolve_all(mock_endpoint) else {
            panic!("accepted invalid demand")
        };
        assert_eq!(
            incomplete.reason(),
            &Failure::InvalidDemand {
                property: Key(2),
                dependency: Key(1)
            }
        );
    }
}

#[test]
fn shared_provider_completes_once() {
    let mut work = Work::new(10.0, HashMap::new());
    add(&mut work, 2, Recipe::Alias(Key(1)));
    add(&mut work, 3, Recipe::Alias(Key(1)));
    add(&mut work, 1, Recipe::Literal(Token::Number(40.0)));
    let (values, effects) = finish(work);
    assert_eq!(values[&Key(2)], values[&Key(3)]);
    assert_eq!(effects.iter().filter(|(key, _)| *key == Key(1)).count(), 1);
}

#[test]
fn error_hides_completed_values_and_effects_until_discard() {
    use std::sync::{
        Arc,
        atomic::{AtomicUsize, Ordering},
    };
    struct Effect(Arc<AtomicUsize>);
    impl Drop for Effect {
        fn drop(&mut self) {
            self.0.fetch_add(1, Ordering::SeqCst);
        }
    }
    let dropped = Arc::new(AtomicUsize::new(0));
    let mut work = Work::new(10.0, HashMap::new());
    add(&mut work, 1, Recipe::Literal(Token::Number(40.0)));
    add(&mut work, 2, Recipe::Error);
    let result = work.resolve_all(|_, name, _, _| {
        if *name == Key(1) {
            Evaluation::Complete {
                value: Token::Number(40.0),
                effects: Effect(dropped.clone()),
            }
        } else {
            Evaluation::Error("second endpoint error")
        }
    });
    let Err(incomplete) = result else {
        panic!("published partial values")
    };
    assert_eq!(dropped.load(Ordering::SeqCst), 0);
    incomplete.discard();
    assert_eq!(dropped.load(Ordering::SeqCst), 1);
}

#[test]
fn borrowed_current_context_is_retained_until_completion() {
    let current = 17;
    let mut work = WinningProviders::<_, Key, usize, ()>::new(&current, HashMap::new());
    assert!(work.admit(Key(1), Winner::Pending(())).is_ok());
    let Ok(completed) =
        work.resolve_all(|context, _, _, _| Evaluation::<Key, _, (), ()>::Complete {
            value: **context,
            effects: (),
        })
    else {
        panic!("failed")
    };
    let (context, values, _) = completed.into_parts();
    assert!(std::ptr::eq(context, &current));
    assert_eq!(values[&Key(1)], 17);
}
