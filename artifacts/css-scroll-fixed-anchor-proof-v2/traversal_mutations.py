import re

CHANGES = [
    ('excluded-descends',
     '| .exclude => prepend [event, .decision id d] (nativeSlots r g children rest)',
     '| .exclude => prepend [event, .decision id d] (children id)'),
    ('omit-skipped-list-event',
     'else prepend [.skip parent kind] (nativeFirst r g children parent rest)',
     'else nativeFirst r g children parent rest'),
    ('reverse-first-lists',
     'let first := nativeFirst r g children parent (g parent).lists',
     'let first := nativeFirst r g children parent (g parent).lists.reverse'),
    ('traverse-no-fallback-value',
     '| none => ⟨some ⟨id, (g id).obs⟩,',
     '| none => ⟨none,'),
    ('identity-requires-ancestry',
     'real == slot || (g real).within', '(g real).within'),
    ('exhaustion-becomes-null',
     '| 0, parent => finished parent ⟨none, [.exhausted parent], true⟩',
     '| 0, parent => finished parent ⟨none, [], false⟩'),
]

PRELUDE = r'''
open Anchor Traversal
def good : Obs := { (default : Obs) with visible := true, full := true }
def node (o : Obs := good) (lists : List (Kind × List Nat) := [])
    (target : Option Nat := none) (within : Bool := true) : Node := ⟨o, lists, target, within⟩
def excludedGraph (id : Nat) : Node :=
  if id == 0 then node good [(.principal, [1,3])]
  else if id == 1 then node {good with fixed := true} [(.principal, [2])]
  else node
def skippedGraph (id : Nat) : Node :=
  if id == 0 then node good [(.float, [2]), (.principal, [1])] else node
def orderedGraph (id : Nat) : Node :=
  if id == 0 then node good [(.principal, [1]), (.fixed, [2])] else node
def fallbackGraph (id : Nat) : Node :=
  if id == 0 then node good [(.principal, [1])]
  else node {good with full := false}
def identityGraph (id : Nat) : Node :=
  if id == 0 then node good [(.principal, [1,2])]
  else if id == 1 then node {good with fixed := true} [] (some 1) false
  else node
def showOutcome (out : Outcome) : IO Unit := IO.println s!"{resultCode out}|{traceCode out.trace}"
'''

WITNESSES = {
    'excluded-descends': (
        '#eval showOutcome (nativeFrame true excludedGraph 4 0)',
        '3|E0;L0:0:0;R1:1:1;D1:0;R3:3:1;D3:3;U3:3;F0:3:0\n',
        '2|E0;L0:0:0;R1:1:1;D1:0;E1;L1:0:0;R2:2:1;D2:3;U2:2;F1:2:0;F0:2:0\n'),
    'omit-skipped-list-event': (
        '#eval showOutcome (nativeFrame true skippedGraph 3 0)',
        '1|E0;K0:2;L0:0:0;R1:1:1;D1:3;U1:1;F0:1:0\n',
        '1|E0;L0:0:0;R1:1:1;D1:3;U1:1;F0:1:0\n'),
    'reverse-first-lists': (
        '#eval showOutcome (nativeFrame true orderedGraph 3 0)',
        '1|E0;L0:0:0;R1:1:1;D1:3;U1:1;F0:1:0\n',
        '2|E0;L0:0:4;R2:2:1;D2:3;U2:2;F0:2:0\n'),
    'traverse-no-fallback-value': (
        '#eval showOutcome (nativeFrame true fallbackGraph 3 0)',
        '1|E0;L0:0:0;R1:1:1;D1:2;N1;E1;L1:1:1;F1:-1:0;B1;U1:1;F0:1:0\n',
        '-1|E0;L0:0:0;R1:1:1;D1:2;N1;E1;L1:1:1;F1:-1:0;B1;U1:1;L0:1:1;F0:-1:0\n'),
    'identity-requires-ancestry': (
        '#eval showOutcome (nativeFrame true identityGraph 3 0)',
        '2|E0;L0:0:0;R1:1:1;D1:0;R2:2:1;D2:3;U2:2;F0:2:0\n',
        '2|E0;L0:0:0;R1:1:0;R2:2:1;D2:3;U2:2;F0:2:0\n'),
    'exhaustion-becomes-null': (
        '#eval showOutcome (nativeFrame true orderedGraph 0 0)',
        '-1|E0;X0;F0:-1:1\n',
        '-1|E0;F0:-1:0\n'),
}


def definitions(source):
    starts = list(re.finditer(r'^(?:theorem|def|abbrev|structure|inductive|end)\b', source, re.M))
    spans = [(m.start(), starts[i + 1].start() if i + 1 < len(starts) else len(source))
             for i, m in enumerate(starts) if source[m.start():].startswith('theorem ')]
    assert len(spans) >= 30
    for start, end in reversed(spans):
        source = source[:start] + source[end:]
    assert not re.search(r'^theorem\b', source, re.M)
    return source.replace('import Anchor', 'import Anchor\nset_option linter.unusedVariables false', 1)


def executable(source, name):
    return definitions(source) + PRELUDE + '\n' + WITNESSES[name][0] + '\n'
