/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use std::collections::{HashMap, hash_map::Entry};
use std::hash::Hash;

pub enum Winner<V, R> {
    Ready(V),
    Pending(R),
}

pub enum Provider<'a, V> {
    Ready(&'a V),
    Missing,
    Pending,
}

pub struct ProviderView<'a, N, V, R> {
    winners: &'a HashMap<N, Winner<V, R>>,
    base: &'a HashMap<N, V>,
}

impl<N: Eq + Hash, V, R> ProviderView<'_, N, V, R> {
    pub fn pending_names(&self) -> impl Iterator<Item = &N> {
        self.winners
            .iter()
            .filter_map(|(name, winner)| matches!(winner, Winner::Pending(_)).then_some(name))
    }

    pub fn ready_values(&self) -> impl Iterator<Item = (&N, &V)> {
        self.base
            .iter()
            .filter(|(name, _)| !self.winners.contains_key(*name))
            .chain(
                self.winners
                    .iter()
                    .filter_map(|(name, winner)| match winner {
                        Winner::Ready(value) => Some((name, value)),
                        Winner::Pending(_) => None,
                    }),
            )
    }

    pub fn get(&self, name: &N) -> Provider<'_, V> {
        match self.winners.get(name) {
            Some(Winner::Ready(value)) => Provider::Ready(value),
            Some(Winner::Pending(_)) => Provider::Pending,
            None => match self.base.get(name) {
                Some(value) => Provider::Ready(value),
                None => Provider::Missing,
            },
        }
    }
}

pub enum Evaluation<N, V, Effects, Error> {
    Complete { value: V, effects: Effects },
    Need(N),
    Error(Error),
}

#[derive(Debug, Eq, PartialEq)]
pub enum Failure<N, Error> {
    Cycle(Vec<N>),
    Endpoint { property: N, error: Error },
    InvalidDemand { property: N, dependency: N },
}

pub struct WinningProviders<Context, N, V, R> {
    context: Context,
    base: HashMap<N, V>,
    winners: HashMap<N, Winner<V, R>>,
    order: Vec<N>,
}

pub struct CompleteProviders<Context, N, V, Effects> {
    context: Context,
    values: HashMap<N, V>,
    effects: Vec<(N, Effects)>,
}

pub struct IncompleteProviders<Context, N, V, R, Effects, Error> {
    work: WinningProviders<Context, N, V, R>,
    effects: Vec<(N, Effects)>,
    reason: Failure<N, Error>,
}

impl<C, N, V, X> CompleteProviders<C, N, V, X> {
    pub fn into_parts(self) -> (C, HashMap<N, V>, Vec<(N, X)>) {
        (self.context, self.values, self.effects)
    }
}

impl<C, N, V, R, X, E> IncompleteProviders<C, N, V, R, X, E> {
    pub fn reason(&self) -> &Failure<N, E> {
        &self.reason
    }

    pub fn discard(self) {
        let Self { work, effects, .. } = self;
        drop(effects);
        drop(work);
    }
}

impl<C, N: Clone + Eq + Hash, V, R> WinningProviders<C, N, V, R> {
    pub fn new(context: C, already_computed: HashMap<N, V>) -> Self {
        Self {
            context,
            base: already_computed,
            winners: HashMap::new(),
            order: Vec::new(),
        }
    }

    // The caller has already applied the real priority/revert/seen gates.
    pub fn admit(&mut self, name: N, winner: Winner<V, R>) -> Result<(), Winner<V, R>> {
        match self.winners.entry(name.clone()) {
            Entry::Occupied(_) => Err(winner),
            Entry::Vacant(entry) => {
                entry.insert(winner);
                self.order.push(name);
                Ok(())
            }
        }
    }

    // Every retry must use a fresh, discardable endpoint context. Effects stay private
    // until every winner has completed; errors never yield a publishable map.
    pub fn resolve_all<X, E>(
        mut self,
        mut evaluate: impl FnMut(&C, &N, &R, &ProviderView<'_, N, V, R>) -> Evaluation<N, V, X, E>,
    ) -> Result<CompleteProviders<C, N, V, X>, IncompleteProviders<C, N, V, R, X, E>> {
        let mut effects = Vec::new();
        let mut stack = Vec::new();
        let mut active = HashMap::new();
        for root in self.order.clone() {
            if matches!(self.winners.get(&root), Some(Winner::Ready(_))) {
                continue;
            }
            stack.push(root.clone());
            active.insert(root, 0);
            while let Some(name) = stack.last().cloned() {
                let step = match self.winners.get(&name) {
                    Some(Winner::Pending(recipe)) => evaluate(
                        &self.context,
                        &name,
                        recipe,
                        &ProviderView {
                            winners: &self.winners,
                            base: &self.base,
                        },
                    ),
                    _ => unreachable!("only unresolved admitted winners enter the work stack"),
                };
                let reason = match step {
                    Evaluation::Complete {
                        value,
                        effects: local_effects,
                    } => {
                        self.winners.insert(name.clone(), Winner::Ready(value));
                        effects.push((name.clone(), local_effects));
                        stack.pop();
                        active.remove(&name);
                        continue;
                    }
                    Evaluation::Need(dependency) => {
                        if !matches!(self.winners.get(&dependency), Some(Winner::Pending(_))) {
                            Failure::InvalidDemand {
                                property: name,
                                dependency,
                            }
                        } else if let Some(&start) = active.get(&dependency) {
                            let mut cycle = stack[start..].to_vec();
                            cycle.push(dependency);
                            Failure::Cycle(cycle)
                        } else {
                            active.insert(dependency.clone(), stack.len());
                            stack.push(dependency);
                            continue;
                        }
                    }
                    Evaluation::Error(error) => Failure::Endpoint {
                        property: name,
                        error,
                    },
                };
                return Err(IncompleteProviders {
                    work: self,
                    effects,
                    reason,
                });
            }
        }
        let mut values = self.base;
        for (name, winner) in self.winners {
            let Winner::Ready(value) = winner else {
                unreachable!("all admitted roots completed")
            };
            values.insert(name, value);
        }
        Ok(CompleteProviders {
            context: self.context,
            values,
            effects,
        })
    }
}
