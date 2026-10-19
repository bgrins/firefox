import itertools
from fractions import Fraction

OPS = ['add', 'subtract', 'intersect', 'exclude']
STATES = [(1,0,1,1,1), (1,1,1,1,1), (0,0,1,1,1), (0,1,1,1,1),
          (1,0,0,1,1), (1,0,1,0,1), (1,0,1,1,0), (1,1,0,0,0)]


def alpha(op, source, dest):
    return [source + dest * (1-source), source*(1-dest), source*dest,
            source*(1-dest)+dest*(1-source)][op]


def outcome(state):
    ref, empty, alloc, valid, snapshot = state
    if not ref:
        return 'reference'
    if empty:
        return 'empty'
    if not alloc or not valid:
        return 'allocation'
    if not snapshot:
        return 'snapshot'
    return 'surface'


def callee_trace(state, mode, mask_type, children):
    result = outcome(state)
    trace = ['reference']
    if result == 'reference':
        return trace
    trace += ['area']
    if result == 'empty':
        return trace
    trace += ['allocate']
    if result == 'allocation':
        return trace
    if children:
        trace += ['child']
    trace += ['luminance' if mode == 2 or (mode == 0 and mask_type == 1) else 'snapshot']
    return trace


def fixtures():
    cases = []
    for state, mode, mask_type, children, output, initial, source, opacity in itertools.product(
            STATES, range(3), range(2), range(2), range(2), range(2), [0, Fraction(1,2), 1], [Fraction(1,2),1]):
        linear = (mode + mask_type + children) % 2
        args = [*state, mode, mask_type, linear, children, output, initial, float(source), float(opacity)]
        result = outcome(state)
        expected_surface = int(result == 'surface')
        expected_alpha = source * opacity if result == 'surface' and children else Fraction(0) if result == 'surface' else Fraction(-1)
        flag = int(result == 'empty') if output else initial
        cases.append({'input': 'callee ' + ' '.join(map(str,args)), 'kind':'callee',
                      'candidate': [expected_surface,flag,expected_alpha],
                      'original': [expected_surface,initial,expected_alpha],
                      'trace':callee_trace(state,mode,mask_type,children)})
    configurations = []
    for state, op, mode, initial in itertools.product(STATES,range(4),range(3),[0,Fraction(1,2),1]):
        configurations.append(([(state,op,mode,Fraction(1,2))],initial))
    for empty_state, middle_op, upper_op, mode, lower_alpha, upper_alpha in itertools.product(
            [STATES[1],STATES[3],STATES[4],STATES[6]],range(4),range(4),range(3),[0,Fraction(1,2),1],[0,Fraction(1,2),1]):
        configurations.append(([(STATES[0],upper_op,mode,upper_alpha),
                               (empty_state,middle_op,mode,1),
                               (STATES[0],0,mode,lower_alpha)],0))
    for index,(layers,initial) in enumerate(configurations):
        ox,oy=[(9,13),(-7,3),(0,0)][index%3]
        tx,ty=[(17,23),(-11,5),(0,0)][index%3]
        args=[len(layers),float(initial),ox,oy,tx,ty]
        expected={};traces={}
        for state,op,mode,source in layers:
            args.extend([*state,mode,0,0,1,op,float(source)])
        for revised in [False,True]:
            dest=Fraction(initial);trace=[]
            for reverse_index,(state,op,mode,source) in enumerate(reversed(layers)):
                effective=0 if reverse_index==0 else op
                trace+=callee_trace(state,mode,0,1)
                result=outcome(state)
                if result=='surface':
                    trace+=['transform:0,0',f'mask:{effective}',f'transform:{tx},{ty}']
                    dest=alpha(effective,source,dest)
                elif revised and result=='empty' and effective in [1,2]:
                    trace+=['transform:0,0',f'clear:{ox},{oy},40,40',f'transform:{tx},{ty}'];dest=Fraction(0)
            key='candidate' if revised else 'original'
            expected[key]=[1,dest,tx,ty];traces[key]=trace
        cases.append({'kind':'stack','input':'stack '+' '.join(map(str,args)),**expected,
                      'traces':traces,'layers':layers,'initial':initial})
    return cases
