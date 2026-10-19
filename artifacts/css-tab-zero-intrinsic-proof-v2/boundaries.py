MAXIMUM = (1 << 30) - 1
INT_MAX = (1 << 31) - 1


def validate_negative(c):
    assert c['mode'] in (1, 2) and c['kind'] == 1
    assert c['width'] == 20 and c['letter'] in (-21, -30, -40)
    assert c['minimum'] in (0, 10) and c['model'] == c['flags'] == 0
    assert -1 in c['tokens'] and all(t in (-1, 40) for t in c['tokens'])
    assert c['width'] / 20 >= 0
    assert c['width'] / 20 * (20 + c['letter']) < 0
    assert abs(c['initial']) + sum(abs(t) for t in c['tokens']) + 1000 < MAXIMUM


def validate_saturation(c):
    assert c['mode'] in (1, 2) and c['kind'] == 0
    assert c['minimum'] == c['letter'] == c['flags'] == c['model'] == 0
    assert c['width'] in (0, 20) and all(t in (-1, 20, 40) for t in c['tokens'])
    assert c['begin'] == 0 and c['end'] == len(c['tokens'])
    assert 0 <= c['initial'] <= MAXIMUM
    assert c['initial'] + sum(max(0, t) for t in c['tokens']) + 20 < INT_MAX
    ranges = [(c['begin'], c['end'])] if c['split'] < 0 else [
        (c['begin'], c['split']), (c['split'], c['end'])]
    current = c['initial']
    branches = []
    for begin, end in ranges:
        pending = 0
        count = 0
        for token in c['tokens'][begin:end] + [None]:
            if token is not None and token >= 0:
                pending += token
                count += 1
                assert pending < MAXIMUM
                continue
            if count:
                assert 0 <= current + pending < INT_MAX
                if current == MAXIMUM:
                    branches.append('infinity')
                elif current + pending > MAXIMUM:
                    branches.append('cap')
                current = min(MAXIMUM, current + pending)
                pending = count = 0
            if token == -1 and c['width']:
                current = ((current + c['width'] - 1) // c['width']) * c['width']
                assert 0 <= current <= MAXIMUM
    assert branches
    return {'branches': branches, 'final': current}


def check_results(cases, actual):
    negative = [c for c in cases if c['domain'] == 'negative-intrinsic']
    saturated = [c for c in cases if c['domain'] == 'saturation']
    result = {'negative_intrinsic': {}, 'saturation': {}}
    for mode in (1, 2):
        neg = [c for c in negative if c['mode'] == mode]
        sat = [c for c in saturated if c['mode'] == mode]
        neg_witnesses = []
        branches = set()
        sat_witnesses = []
        mutant = 'minimum_loses_saturation' if mode == 1 else 'preferred_loses_saturation'
        for c in neg:
            validate_negative(c)
            i = c['id']
            assert actual['original'][i] == actual['candidate'][i]
            events = actual['candidate'][i]['events']
            tab_count = c['tokens'].count(-1)
            ranges = [(c['begin'], c['end'])] if c['split'] < 0 else [
                (c['begin'], c['split']), (c['split'], c['end'])]
            batches = 0
            for begin, end in ranges:
                in_glyphs = False
                for token in c['tokens'][begin:end]:
                    if token != -1 and not in_glyphs:
                        batches += 1
                    in_glyphs = token != -1
            assert sum(e[0] == 22 for e in events) == 2 * tab_count + batches
            if actual['nonpositive_guard'][i] != actual['candidate'][i]:
                neg_witnesses.append(i)
        for c in sat:
            checked = validate_saturation(c)
            branches.update(checked['branches'])
            i = c['id']
            assert actual['original'][i] == actual['candidate'][i]
            assert actual['candidate'][i]['state'][0] == checked['final'] == MAXIMUM
            if actual[mutant][i] != actual['candidate'][i]:
                sat_witnesses.append(i)
        assert neg_witnesses and sat_witnesses
        assert branches == {'cap', 'infinity'}
        result['negative_intrinsic'][mode] = {
            'cases': len(neg), 'nonpositive_guard_witnesses': neg_witnesses,
            'recomputed_numeric_width_calls_checked': True,
        }
        result['saturation'][mode] = {
            'cases': len(sat), 'branches': sorted(branches),
            'no_saturation_mutant_witnesses': sat_witnesses,
            'all_additions_and_casts_defined': True,
        }
    return result
