import re

CHANGES = [
    ('fixed', '(repaired && o.fixed)', '(false && o.fixed)'),
    ('sticky', '|| o.sticky ||', '|| false ||'),
    ('exclude-traverses', '| .exclude => select r rest', '| .exclude => select r children'),
    ('pass-fallback', '| .pass => (select r children).orElse (fun _ => select r rest)',
     '| .pass => (select r children).orElse (fun _ => some p)'),
    ('absolute-order', 'firstPass lists ++ absolutePass lists', 'absolutePass lists ++ firstPass lists'),
    ('maintenance', 'if maintain g then select r tree else none', 'select r tree'),
]

PRELUDE = r'''
open Anchor

def visible : Obs := { (default : Obs) with visible := true, full := true }
def leaf (id : Nat) : Plan := .step ⟨id, visible⟩ .nil .nil
def excluded (sticky : Bool) : Plan :=
  .step ⟨1, { visible with fixed := !sticky, sticky := sticky }⟩ (leaf 2) (leaf 3)
def inlineEmpty : Plan :=
  .step ⟨1, { visible with inlineBox := true }⟩ .nil (leaf 3)
def orderedGraph (id : Nat) : Node :=
  ⟨visible, if id == 0 then [(.absolute, [2]), (.principal, [1])] else [], none, true⟩
def orderedTree : Plan := unfoldGraph orderedGraph 3 (successors orderedGraph 0)
def selectedCode (p : Option Pick) : Int := (p.map (fun x => (x.id : Int))).getD (-1)
def showTree (t : Plan) : IO Unit :=
  IO.println s!"{selectedCode (select true t)}|{String.intercalate "," ((visits true t).map toString)}"
'''

WITNESSES = {
    'fixed': ('#eval showTree (excluded false)', '3|1,3\n', '1|1\n',
              'Fully visible fixed parent 1 has child 2 and following sibling 3.'),
    'sticky': ('#eval showTree (excluded true)', '3|1,3\n', '1|1\n',
               'Fully visible sticky parent 1 has child 2 and following sibling 3.'),
    'exclude-traverses': ('#eval showTree (excluded false)', '3|1,3\n', '2|1,3\n',
                         'Excluded parent must skip child 2 and choose sibling 3; selection mutation alone leaves visits unchanged.'),
    'pass-fallback': ('#eval showTree inlineEmpty', '3|1,3\n', '1|1,3\n',
                      'Empty non-replaced inline parent passes through to sibling 3, never selecting itself.'),
    'absolute-order': ('#eval showTree orderedTree', '1|1\n', '2|2\n',
                       'Principal child 1 precedes absolute child 2 even when absolute list is stored first.'),
    'maintenance': ('#eval IO.println (selectedCode (publicSelect ⟨false, false, false, false, false⟩ true (leaf 1)))',
                    '-1\n', '1\n', 'Disabled preference forbids selecting otherwise acceptable child 1.'),
}


def definitions(source):
    starts = list(re.finditer(r'^(?:theorem|def|abbrev|structure|inductive|end)\b', source, re.M))
    spans = [(m.start(), starts[i + 1].start() if i + 1 < len(starts) else len(source))
             for i, m in enumerate(starts) if source[m.start():].startswith('theorem ')]
    assert len(spans) == 48
    for start, end in reversed(spans):
        source = source[:start] + source[end:]
    assert not re.search(r'^theorem\b', source, re.M)
    return source


def executable(source, name):
    return definitions(source).replace('import Std', 'import Std\nset_option linter.unusedVariables false', 1) + PRELUDE + '\n' + WITNESSES[name][0] + '\n'
