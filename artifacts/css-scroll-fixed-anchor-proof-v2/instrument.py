import hashlib

import bridge


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def recover(items, changes):
    restored = items.copy()
    for edit in reversed(changes):
        item = edit['item']
        current = restored[item]
        assert digest(current) == edit['after_sha256'], item
        assert current.count(edit['new']) == edit['occurrences'], item
        current = current.replace(edit['new'], edit['old'])
        assert digest(current) == edit['before_sha256'], item
        assert current.count(edit['old']) == edit['occurrences'], item
        restored[item] = current
    return restored


def generate(candidate=True):
    snippets, enum, helpers = bridge.extract(candidate)
    originals = snippets.copy()
    changes = []

    def change(item, old, new, count=1):
        before = snippets[item]
        assert before.count(old) == count, (item, old, before.count(old))
        after = before.replace(old, new)
        changes.append(dict(item=item, old=old, new=new, occurrences=count,
                            before_sha256=digest(before), after_sha256=digest(after)))
        snippets[item] = after

    frame = bridge.ITEMS[4]
    slots = bridge.ITEMS[5]
    public = bridge.ITEMS[2]
    change(frame, ') const {', ') const {\n  sem("E", sid(aFrame));')
    change(frame, '      continue;', '      sem("K", sid(aFrame), static_cast<int>(listID));\n      continue;')
    change(frame, '    // Search the child list',
           '    sem("L", sid(aFrame), 0, static_cast<int>(listID));\n    // Search the child list')
    change(frame, 'if (nsIFrame* anchor = FindAnchorInList(absPosList))',
           'sem("L", sid(aFrame), 1, 1);\n  if (nsIFrame* anchor = FindAnchorInList(absPosList))')
    change(frame, 'return anchor;', 'sem("F", sid(aFrame), sid(anchor), 0);\n    return anchor;', 2)
    change(frame, 'return nullptr;', 'sem("F", sid(aFrame), -1, 0);\n  return nullptr;')
    change(slots, '        continue;\n      }\n      ANCHOR_LOG(',
           '        sem("R", sid(child), sid(realFrame), 0);\n        continue;\n      }\n      ANCHOR_LOG(')
    change(slots, '      child = realFrame;\n    }',
           '      sem("R", sid(child), sid(realFrame), 1);\n      child = realFrame;\n    } else {\n      sem("R", sid(child), sid(realFrame), 1);\n    }')
    change(slots, 'ExamineResult examine = ExamineAnchorCandidate(child);',
           'ExamineResult examine = ExamineAnchorCandidate(child);\n    sem("D", sid(child), static_cast<int>(examine));')
    change(slots, 'nsIFrame* candidate = FindAnchorIn(child);',
           'sem("N", sid(child));\n        nsIFrame* candidate = FindAnchorIn(child);', 2)
    change(slots, 'if (!candidate) {\n          return child;\n        }',
           'if (!candidate) {\n          sem("B", sid(child));\n          sem("U", sid(child), sid(child));\n          return child;\n        }')
    change(slots, 'return candidate;', 'sem("U", sid(child), sid(candidate));\n        return candidate;', 2)
    change(slots, 'case ExamineResult::Accept: {\n        return child;',
           'case ExamineResult::Accept: {\n        sem("U", sid(child), sid(child));\n        return child;')
    change(public, '  mAnchorMightBeSubOptimal =',
           '  sem("Z", sid(mAnchorNode));\n  mAnchorMightBeSubOptimal =')

    original_adapter = (bridge.ROOT / 'adapter.cpp').read_text()
    adapter = original_adapter
    adapter_changes = []

    def change_adapter(old, new):
        nonlocal adapter
        assert adapter.count(old) == 1, old
        after = adapter.replace(old, new)
        adapter_changes.append(dict(item='adapter', old=old, new=new, occurrences=1,
                                    before_sha256=digest(adapter), after_sha256=digest(after)))
        adapter = after
    additions = r'''
std::vector<std::string> semantic;
template<typename... Args> void sem(const char* code, Args... fields) {
  std::string value(code);
  bool first = true;
  ((value += (std::exchange(first, false) ? "" : ":") + std::to_string(fields)), ...);
  semantic.push_back(value);
}
'''
    change_adapter('std::vector<std::string> events;',
                              'std::vector<std::string> events;\n' + additions)
    change_adapter('struct nsPlaceholderFrame : nsIFrame {',
        'int sid(const nsIFrame* frame) { return frame ? frame->id : -1; }\nstruct nsPlaceholderFrame : nsIFrame {')
    change_adapter('    events.clear();', '    events.clear(); semantic.clear();')
    old = 'result = static_cast<int>(a.ExamineAnchorCandidate(owned[2].get()));'
    change_adapter(old, old + ' sem("D", 2, result);')
    old = "std::cout << '\\n';"
    change_adapter(old, "std::cout << '|'; for (const auto& e : semantic) std::cout << e << ';'; " + old)
    restored = recover(snippets, changes)
    restored_adapter = recover({'adapter': adapter}, adapter_changes)['adapter']
    assert restored == originals and restored_adapter == original_adapter
    for token in ['/*EXAMINE_ENUM*/', '/*PLACEHOLDER_HELPERS*/', '/*EXTRACTED_FUNCTIONS*/']:
        assert adapter.count(token) == restored_adapter.count(token) == 1
    recovered_source = restored_adapter.replace('/*EXAMINE_ENUM*/', enum).replace(
        '/*PLACEHOLDER_HELPERS*/', helpers).replace(
        '/*EXTRACTED_FUNCTIONS*/', '\n\n'.join(restored.values()))
    assert recovered_source == bridge.generate(candidate)
    source = adapter.replace('/*EXAMINE_ENUM*/', enum).replace(
        '/*PLACEHOLDER_HELPERS*/', helpers).replace(
        '/*EXTRACTED_FUNCTIONS*/', '\n\n'.join(snippets.values()))
    return source, dict(variant='candidate' if candidate else 'original',
                        adapter_original_sha256=digest((bridge.ROOT / 'adapter.cpp').read_text()),
                        adapter_instrumented_sha256=digest(adapter), changes=changes,
                        adapter_changes=adapter_changes, recovery_verified=True,
                        recovered_source_sha256=digest(recovered_source),
                        instrumented_snippets=snippets, instrumented_adapter=adapter)
