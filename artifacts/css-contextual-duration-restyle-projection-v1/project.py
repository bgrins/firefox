import copy
import math
import re

SELECTOR = 'dom/animation/test/mozilla/test_restyles.html'
TEMPLATES = {
    24: 'Transform animation running on the element which is scrolled out should be throttled until 200ms is elapsed.',
    25: 'Transform animation running on the element which is scrolled out should be unthrottled after around 200ms have elapsed.',
    27: 'Transform animation running on out of view element should be throttled until 200ms is elapsed.',
    28: 'Transform animation running on out of view element should be unthrottled after around 200ms have elapsed.',
}
NUMBER = r'(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?'


def project(assessment):
    result = copy.deepcopy(assessment)
    assert result['assertion_count'] == len(result['assertions']) == 170
    for index, text in TEMPLATES.items():
        row = result['assertions'][index]
        assert row['action'] == 'test_status' and row['test'] == SELECTOR
        assert row['status'] == row['expected_effective'] == 'PASS'
        gap = '' if index in (24, 27) else ' '
        pattern = re.escape(text) + r' now: (' + NUMBER + r') start time: (' + NUMBER + r') elapsed:' + gap + '(' + NUMBER + ')'
        match = re.fullmatch(pattern, row['message'])
        assert match is not None
        now, start, elapsed = map(float, match.groups())
        assert all(math.isfinite(value) and value >= 0 for value in (now, start, elapsed))
        assert now >= start
        tolerance = 8 * sum(math.ulp(value) for value in (now, start, elapsed))
        assert abs(elapsed - (now - start)) <= tolerance
        if index in (24, 27):
            assert float(format(elapsed, '.10g')) >= 200
        row['message'] = text + ' now: <time> start time: <time> elapsed:' + gap + '<duration>'
    return result


def compare(original, candidate):
    return project(original) == project(candidate)
