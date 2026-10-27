import math

PHASES = ['first', 'repeat', 'reset', 'restored']
NUMERIC_STYLE = ['width', 'height', 'paddingTop', 'paddingRight', 'paddingBottom',
                 'paddingLeft', 'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
                 'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
                 'left', 'top']
POLICY_STYLE = ['position', 'display', 'boxSizing', 'overflowX', 'overflowY',
                'transform', 'zoom', 'direction', 'writingMode', 'contain', 'clip']
MEASUREMENT = {'scrollSize', 'clientSize', 'clientOrigin', 'rect', 'rects', 'hostRect',
               'style', 'hostStyle', 'parentMatches', 'empty', 'scrollPosition', 'viewport'}


def vector(value, length, integer=False):
    assert type(value) is list and len(value) == length
    assert all(type(v) in ([int] if integer else [int, float]) and math.isfinite(v) for v in value)


def expected_style(width, height, left, top, position, padding=None):
    result = {name: 0 for name in NUMERIC_STYLE}
    result.update(width=width, height=height, left=left, top=top,
                  position=position, display='block', boxSizing='content-box',
                  overflowX='visible', overflowY='visible', transform='none', zoom='1',
                  direction='ltr', writingMode='horizontal-tb', contain='none', clip='auto')
    if padding:
        result[padding[0]] = padding[1]
    return result


def validate(payload):
    assert type(payload) is dict and set(payload) == {'compatMode', 'rows'}
    assert payload['compatMode'] == 'CSS1Compat'
    roster = [(axis, base, extra) for axis in ['x', 'y'] for base in [16, 8388600] for extra in [0, 9]]
    assert type(payload['rows']) is list and len(payload['rows']) == len(roster)
    rows = []
    for raw, (axis, base, extra) in zip(payload['rows'], roster):
        assert set(raw) == {'key', 'axis', 'base', 'extra', *PHASES}
        assert (raw['axis'], raw['base'], raw['extra']) == (axis, base, extra)
        assert type(raw['base']) is type(raw['extra']) is int
        assert raw['key'] == f'{axis}-{base}-{extra}'
        phases = {}
        for name in PHASES:
            value = raw[name]
            assert type(value) is dict and set(value) == MEASUREMENT
            for field in ['scrollSize', 'clientSize', 'clientOrigin']:
                vector(value[field], 2, integer=True)
            for field, count in [('rect', 4), ('hostRect', 4), ('scrollPosition', 2), ('viewport', 2)]:
                vector(value[field], count)
            assert type(value['rects']) is list
            for rect in value['rects']:
                vector(rect, 4)
            assert type(value['parentMatches']) is bool and type(value['empty']) is bool
            for field in ['style', 'hostStyle']:
                style = value[field]
                assert type(style) is dict and set(style) == set(NUMERIC_STYLE + POLICY_STYLE)
                assert all(type(style[k]) in [int, float] and math.isfinite(style[k]) for k in NUMERIC_STYLE)
                assert all(type(style[k]) is str for k in POLICY_STYLE)
            padding = 0 if name == 'reset' else extra
            content = [base, 16] if axis == 'x' else [16, base]
            expected = [base + padding, 16] if axis == 'x' else [16, base + padding]
            rect = [40, 40, *expected]
            checks = {
                'parent': value['parentMatches'], 'empty': value['empty'],
                'style': value['style'] == expected_style(*content, 0, 0, 'absolute',
                    ('paddingRight' if axis == 'x' else 'paddingBottom', padding)),
                'host_style': value['hostStyle'] == expected_style(100, 100, 40, 40, 'fixed'),
                'geometry': value['rect'] == rect,
                'single_box_geometry': value['rects'] == [rect],
                'host_geometry': value['hostRect'] == [40, 40, 100, 100],
                'window_scroll': value['scrollPosition'] == [0, 0],
                'viewport': min(value['viewport']) > 140,
            }
            calibrated = all(checks.values())
            phases[name] = {'calibrated': calibrated,
                           'failed_calibration': [k for k, v in checks.items() if not v],
                           'expected_size': expected,
                           'observed_scroll': value['scrollSize'], 'observed_client': value['clientSize'],
                           'scroll_matches': value['scrollSize'] == expected if calibrated else None,
                           'client_matches': value['clientSize'] == expected if calibrated else None,
                           'client_origin_matches': value['clientOrigin'] == [0, 0] if calibrated else None}
        rows.append({'key': raw['key'], 'calibrated': all(v['calibrated'] for v in phases.values()),
                     'repeat_stable': raw['first'] == raw['repeat'],
                     'restored_stable': raw['first'] == raw['restored'], 'phases': phases})
    return {'rows': rows, 'calibrated': sum(r['calibrated'] for r in rows),
            'phase_calibrated': sum(v['calibrated'] for r in rows for v in r['phases'].values()),
            'repeat_stable': sum(r['repeat_stable'] for r in rows),
            'restored_stable': sum(r['restored_stable'] for r in rows),
            'first_scroll_matches': sum(r['phases']['first']['scroll_matches'] is True for r in rows),
            'first_client_matches': sum(r['phases']['first']['client_matches'] is True for r in rows)}
