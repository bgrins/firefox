import copy

FIELDS = ('action','status','message','expected','known_intermittent')

def signatures(assessment, experiment):
    expected = {(test,name) for test,names in (experiment['target_subtests']|experiment['held_subtests']).items() for name in names}
    expected |= {(test,None) for test in experiment['tests']}
    values = {}
    for event in assessment['rows']+assessment['ends']:
        key = (event['test'],event.get('subtest') if event['action']=='test_status' else None)
        if key in values or key not in expected:
            raise ValueError('duplicate or unknown outcome identity')
        values[key] = {field:copy.deepcopy(event[field]) for field in FIELDS if field in event}
    if set(values)!=expected or len(expected)!=699:
        raise ValueError('missing exact668 assertions/31 completions')
    return values


def compare(previous, current, experiment, normalizer, declared):
    raw_left,raw_right = signatures(previous,experiment),signatures(current,experiment)
    raw_changes = [{'test':key[0],'subtest':key[1],'previous':raw_left[key],'current':raw_right[key]} for key in sorted(raw_left,key=str) if raw_left[key]!=raw_right[key]]
    left,right,ports = normalizer.normalize_pair(previous,current,declared)
    a,b = signatures(left,experiment),signatures(right,experiment)
    differences = [{'test':key[0],'subtest':key[1],'previous':a[key],'current':b[key]} for key in sorted(a,key=str) if a[key]!=b[key]]
    focus = {(test,name) for test,names in experiment['focus_subtests'].items() for name in names}
    if len(focus)!=86:
        raise ValueError('exact86 final focused assertions')
    focus_failures = [{'test':test,'subtest':name,'status':raw_right[(test,name)]['status']} for test,name in sorted(focus) if raw_right[(test,name)]['status']!='PASS']
    return {'comparison_complete':True,'test_evidence_supports_acceptance':not differences and not focus_failures,
            'exact_subtest_signatures':668,'exact_test_completions':31,'focused_assertions':86,
            'all86_focused_pass':not focus_failures,'focus_failures':focus_failures,
            'raw_changes':raw_changes,'normalized_differences':differences,'normalization_records':ports,
            'normalization_scope':'Unchanged strict adjudicator:only HTTP ports in six manifest-exact PASS reference completion messages',
            'native_fix_accepted':False,'recommendation_scope':'Test evidence only; root reviews source/spec/triage and commits independently.'}
