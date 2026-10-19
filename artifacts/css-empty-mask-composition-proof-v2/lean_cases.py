from fractions import Fraction


def rat(n):
    n = Fraction(n)
    return f'(({n.numerator} : Rat) / {n.denominator})'


def boolean(n):
    return 'true' if n else 'false'


def generate(cases):
    lines = ['open Mask',
             'def alphaOf : Outcome → Rat | .surface a => a | _ => -1',
             'def surfaceOf : Outcome → Nat | .surface _ => 1 | _ => 0',
             'def boolNum (x : Bool) : Nat := if x then 1 else 0',
             'set_option maxRecDepth 20000',
             'set_option maxHeartbeats 0']
    for index, case in enumerate(cases):
        if case['kind'] == 'callee':
            v = case['input'].split()[1:]
            ref, empty, alloc, valid, snap, mode, typ, linear, child, output, initial = map(int, v[:11])
            value = Fraction(v[11]) * Fraction(v[12]) if child else Fraction(0)
            expr = f'sourceOutcome {boolean(ref)} {boolean(empty)} {boolean(alloc and valid)} {boolean(snap)} {rat(value)}'
            lines.append(f'#eval do\n  let result := {expr}\n  IO.println (toString (surfaceOf result) ++ " " ++ toString (boolNum (writeOutput {boolean(output)} {boolean(initial)} result)) ++ " " ++ toString (alphaOf result))')
        else:
            expr = rat(case['initial'])
            for i,(state,op,mode,value) in enumerate(reversed(case['layers'])):
                ref,empty,alloc,valid,snap = state
                outcome = f'sourceOutcome {boolean(ref)} {boolean(empty)} {boolean(alloc and valid)} {boolean(snap)} {rat(value)}'
                expr = f'dispatch {boolean(i==0)} .{["add","subtract","intersect","exclude"][op]} ({outcome}) ({expr})'
            lines.append(f'#eval IO.println (toString ({expr}))')
    return '\n'.join(lines) + '\n'
