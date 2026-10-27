import json
import math


def classify(rows, roster):
    if [r['subtest'] for r in rows] != roster['tests']:
        raise ValueError('exact ordered ten-case roster')
    output = []
    decoder = json.JSONDecoder()
    controls_pass = all(r['status'] == 'PASS' for r in rows[4:])
    for row, oracle in zip(rows, roster['expectations']):
        result = dict(name=row['subtest'], status=row['status'], message=row.get('message'))
        if row.get('expected') not in (None, 'PASS') or row.get('known_intermittent'):
            raise ValueError('unexpected expectation metadata')
        if row['status'] == 'PASS':
            if row.get('message') not in (None, ''):
                raise ValueError('PASS message')
            result['classification'] = 'PASS_NO_EXPORTED_HISTORY'
        else:
            result['classification'] = 'CALIBRATION_OR_SETUP_INCONCLUSIVE'
            prefix = 'assert_equals: registered endpoint history: '
            message = row.get('message') or ''
            if message.startswith(prefix):
                try:
                    actual, end = decoder.raw_decode(message[len(prefix):])
                    tail = message[len(prefix) + end:]
                    assert tail.startswith(' expected ')
                    expected_text, end = decoder.raw_decode(tail[len(' expected '):])
                    tail = tail[len(' expected ') + end:]
                    assert tail.startswith(' but got ')
                    actual_text, end = decoder.raw_decode(tail[len(' but got '):])
                    assert not tail[len(' but got ') + end:]
                    expected = json.loads(expected_text)
                    assert json.loads(actual_text) == actual
                    assert len(actual) == len(expected) == len(oracle['values'])
                    for i, (sample, wanted) in enumerate(zip(actual, expected)):
                        provider_index = i // 3
                        pt = [250, 750, 250][provider_index] if len(actual) == 9 else None
                        shape = dict(providerTime=pt, consumerTime=[0, 500, 1000][i % 3],
                                     first=oracle['values'][i], repeated=oracle['values'][i], provider=oracle['providers'][provider_index])
                        assert wanted == shape and set(sample) == set(shape)
                        assert all(sample[k] == shape[k] for k in ('providerTime', 'consumerTime', 'provider'))
                        assert all(type(sample[k]) in (int, float) and math.isfinite(sample[k]) for k in ('first', 'repeated'))
                    assert actual != expected
                    result.update(actual=actual, expected=expected, classification=
                        'CALIBRATED_FINAL_HISTORY_MISMATCH' if controls_pass else 'HISTORY_MISMATCH_WITH_FAILED_CONTROLS')
                except (AssertionError, ValueError, TypeError, KeyError, IndexError) as error:
                    result['parse_error'] = repr(error)
        output.append(result)
    return dict(rows=output, static_controls_pass=controls_pass,
                pass_count=sum(r['status'] == 'PASS' for r in rows),
                fail_count=sum(r['status'] == 'FAIL' for r in rows),
                expected_failure_count=None, pass_histories_exported=False)
