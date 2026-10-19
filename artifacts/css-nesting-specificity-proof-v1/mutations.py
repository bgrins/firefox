from pathlib import Path

BASE = Path(__file__).resolve().parent

def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

def variants():
    parser = (BASE / "optimized-source-v2/parser.rs").read_text()
    builder = (BASE / "optimized-source-v2/builder.rs").read_text()
    out = {}
    direct = "                    specificity += Specificity::from(parent_specificity_and_flags.specificity);"
    out["missing-direct-parent"] = (once(parser, direct, ""), builder)
    out["double-direct-parent"] = (once(parser, direct, direct + "\n" + direct), builder)
    out["recomputed-forbidden-flags"] = (once(parser,
        "            specificity: specificity.into(),\n            flags,\n        };\n        Selector(items.shareable())",
        "            specificity: specificity.into(),\n            flags: specificity_and_flags(items.slice().iter(), false).flags,\n        };\n        Selector(items.shareable())"), builder)
    out["where-contributes"] = (parser, once(builder,
        "if !matches!(*simple_selector, Component::Where(..)) {", "if true {"))
    out["missing-host-offset"] = (parser, once(builder,
        "flags.insert(SelectorFlags::HAS_HOST);\n                specificity.class_like_selectors += 1;",
        "flags.insert(SelectorFlags::HAS_HOST);"))
    out["missing-slotted-offset"] = (parser, once(builder,
        "                    specificity.element_selectors += 1;", ""))
    out["missing-nth-offset"] = (parser, once(builder,
        "                specificity.class_like_selectors += 1;\n                let sf = selector_list_specificity_and_flags(",
        "                let sf = selector_list_specificity_and_flags("))
    helper = """        fn with_specificity<Impl: SelectorImpl>(s: &Selector<Impl>, value: u32) -> Selector<Impl> {
            Selector::from_vec(s.iter_raw_parse_order_from(0).cloned().collect(), value, s.flags())
        }

"""
    marked = once(parser, "        fn replace_parent_on_selector_list<Impl: SelectorImpl>(", helper + "        fn replace_parent_on_selector_list<Impl: SelectorImpl>(")
    old = """            flags.insert(result_specificity_and_flags.flags - forbidden_flags);
            Some(result)"""
    new = """            let old = selector_list_specificity_and_flags(orig.iter(), false).specificity;
            let corrupt: u32 = (Specificity::from(old) + Specificity::from(result_specificity_and_flags.specificity - old)).into();
            let result = SelectorList::from_iter(result.slice().iter().map(|s| {
                if s.specificity() == result_specificity_and_flags.specificity { with_specificity(s, corrupt) } else { s.clone() }
            }));
            flags.insert(result_specificity_and_flags.flags - forbidden_flags);
            Some(result)"""
    out["packed-delta-list-maximum"] = (once(marked, old, new), builder)
    old = """            flags.insert(result_specificity_and_flags.flags - forbidden_flags);
            result
"""
    new = """            let old = relative_selector_list_specificity_and_flags(orig, false).specificity;
            let corrupt: u32 = (Specificity::from(old) + Specificity::from(result_specificity_and_flags.specificity - old)).into();
            let result = result.into_iter().map(|mut rel| {
                if rel.selector.specificity() == result_specificity_and_flags.specificity {
                    rel.selector = with_specificity(&rel.selector, corrupt);
                }
                rel
            }).collect();
            flags.insert(result_specificity_and_flags.flags - forbidden_flags);
            result
"""
    out["packed-delta-relative-maximum"] = (once(marked, old, new), builder)
    old = "            let new_selector = orig.replace_parent_selector(parent);"
    new = """            let new_selector = orig.replace_parent_selector(parent);
            let corrupt: u32 = (Specificity::from(orig.specificity()) + Specificity::from(new_selector.specificity() - orig.specificity())).into();
            let new_selector = with_specificity(&new_selector, corrupt);"""
    out["packed-delta-single-wrapper"] = (once(marked, old, new), builder)
    return out

if __name__ == "__main__":
    for name, (parser, builder) in variants().items():
        out = BASE / "mutant-sources" / name
        out.mkdir(parents=True, exist_ok=True)
        (out / "parser.rs").write_text(parser)
        (out / "builder.rs").write_text(builder)
