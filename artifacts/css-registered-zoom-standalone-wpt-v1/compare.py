from collections import Counter


def need(value, message):
    if not value:
        raise ValueError(message)


def signatures(events, experiment):
    expected = {(test,name) for test,names in dict(experiment['target_subtests'],**experiment['held_subtests']).items() for name in names}
    result = {}
    for event in events:
        key = (event['test'],event.get('subtest') if event['action'] == 'test_status' else None)
        need(key not in result, 'duplicate outcome identity')
        need((key in expected if key[1] is not None else key[0] in experiment['tests']), 'unknown outcome identity')
        result[key] = {name:event[name] for name in ['action','status','message','expected','known_intermittent'] if name in event}
    need(set(result) == expected | {(name,None) for name in experiment['tests']}, 'missing outcome identity')
    need(len(expected) == 636 and len(experiment['tests']) == 29, 'fixed 636 plus 29 completions')
    return result


def compare(original, current, experiment, historical):
    need(current['complete'] and current['execution_preserved'], 'complete preserved current phase')
    right = signatures(current['rows']+current['ends'],experiment)
    past = signatures(historical['events'],experiment)
    left = signatures(original['rows']+original['ends'],experiment) if original else None
    if original:
        need(original['complete'] and original['execution_preserved'], 'complete preserved original phase')
        a,b = dict(original['run_info']),dict(current['run_info'])
        a.pop('browser_build_id');b.pop('browser_build_id')
        need(a == b and original['run_binding']['revision'] == current['run_binding']['revision'] == experiment['frozen_head'], 'paired run_info outside bound BuildID drift')
    rows, bad, counts, completions = [], [], Counter(), Counter()
    for key in sorted(right,key=lambda k:(k[0],k[1] or '')):
        now, old, combined = right[key],left[key] if left else None,past[key]
        family = 'broad' if key[0] in experiment['broad_tests'] else 'zoom70'
        category = 'baseline_observation' if old is None else (
            'unchanged' if old == now else 'repaired' if old['status'] == 'FAIL' and now['status'] == 'PASS' else
            'new_failure' if old['status'] in ('PASS','OK') and now['status'] == 'FAIL' else 'changed_unresolved')
        (counts if key[1] is not None else completions)[family+':'+category] += 1
        if family == 'broad' and category in ('new_failure','changed_unresolved'):
            bad.append({'test':key[0],'subtest':key[1],'category':category})
        rows.append({'test':key[0],'subtest':key[1],'family':family,'category':category,
                     'original':old,'current':now,'historical_combined9':combined,
                     'combined9_only_pass':combined['status']=='PASS' and now['status']=='FAIL'})
    return {'complete':True,'broad_regression_gate_passed':original is not None and not bad,
            'broad_rejections':bad,'summary':{'subtests':dict(counts),'test_completions':dict(completions)},'rows':rows,'native_fix_acceptance':False,
            'attribution_limit':'Historical combined9 used the same fixtures in three separate runs; combined9-only PASS indicates a candidate A dependency, not an independent causal proof.'}
