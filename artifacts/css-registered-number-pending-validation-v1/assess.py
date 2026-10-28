import re


def assess(log, expected):
    assert len(expected) == len(set(expected))
    active = None
    seen = {}
    suites = 0
    suite_open = False
    suite_prefix = None
    finished_prefixes = set()
    summaries = []
    for line in log.splitlines():
        if re.search(r'\bSUITE_START: gtest - ', line):
            assert active is None and not suite_open and not summaries
            suites += 1
            suite_open = True
            suite_prefix = None
        start = re.search(r'\bTEST_START: (\S+)\s*$', line)
        if start:
            name = start.group(1)
            assert suite_open and active is None and name in expected and name not in seen
            prefix = name.split('.')[0]
            assert prefix not in finished_prefixes
            assert suite_prefix is None or suite_prefix == prefix
            suite_prefix = prefix
            active = name
        end = re.search(r'\bTEST_END: (\S+)\s*$', line)
        if end:
            assert active is not None and end.group(1) == 'PASS'
            seen[active] = end.group(1)
            active = None
        if re.search(r'\bSUITE_END\s*$', line):
            assert active is None and suite_open and suite_prefix is not None
            finished_prefixes.add(suite_prefix)
            suite_open = False
        summary = re.search(
            r'Ran (\d+) test\(s\) from (\d+) test suite\(s\) \((\d+) disabled\), with (\d+) failure\(s\)\.',
            line,
        )
        if summary:
            assert not suite_open and active is None and set(seen) == set(expected)
            summaries.append(summary.groups())
    assert active is None and not suite_open and set(seen) == set(expected)
    expected_suites = len({name.split('.')[0] for name in expected})
    assert summaries == [(str(len(expected)), str(expected_suites), '0', '0')]
    assert suites == expected_suites
    assert finished_prefixes == {name.split('.')[0] for name in expected}
    assert not re.search(r'\bTEST_UNEXPECTED|\bPROCESS_CRASH', log)
    return {'tests': seen, 'suites': suites, 'all_selected_passed': True}
