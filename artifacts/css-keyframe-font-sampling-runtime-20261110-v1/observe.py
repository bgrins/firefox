import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent


def strict_json(text):
    def pairs(items):
        out={}
        for key,value in items:
            assert key not in out,('duplicate JSON key',key)
            out[key]=value
        return out
    def constant(value):
        raise ValueError('non-JSON numeric constant: '+value)
    return json.loads(text,object_pairs_hook=pairs,parse_constant=constant)


def number(value,nullable=False):
    return nullable and value is None or type(value) in (int,float) and math.isfinite(value)


def validate(row,schema):
    assert type(row) is dict and set(row)==set(schema['required_record_fields'])
    assert type(row['id']) is str and row['id'] in schema['ids']
    assert type(row['phase']) is str and row['phase'] in schema['phases']
    assert type(row['animationType']) is str and row['animationType']
    assert type(row['readySettled']) is bool
    for field in ['before','after']:
        assert type(row[field]) is dict and set(row[field])==set(schema['style_fields'])
        assert all(type(value) is str for value in row[field].values())
    for field in ['stateBefore','stateAfter']:
        state=row[field]
        assert type(state) is dict and set(state)==set(schema['state_fields'])
        assert state['playState'] in ['idle','running','paused','finished'] and type(state['pending']) is bool
        for key in ['currentTime','startTime','progress','localTime','currentIteration']:
            assert number(state[key],True),(field,key)
        for key in ['playbackRate','duration','activeDuration','endTime']:
            assert number(state[key]),(field,key)
    assert type(row['frames']) is list
    for frame in row['frames']:
        assert type(frame) is dict and {'offset','computedOffset','easing','composite'}<=set(frame)
        assert number(frame['offset'],True) and number(frame['computedOffset'])
        assert type(frame['easing']) is str and frame['composite'] in ['auto','replace','add','accumulate']
        assert all(type(v) is str for k,v in frame.items() if k not in ['offset','computedOffset'])


def parse(path):
    schema=strict_json((HERE/'OBSERVATION-SCHEMA.json').read_text())
    records={};phases={name:[] for name in schema['ids']}
    for line in Path(path).read_text().splitlines():
        event=strict_json(line);assert type(event) is dict
        marked=[key for key in ['data','message'] if type(event.get(key)) is str and 'KFONT' in event[key]]
        if not marked:continue
        assert event.get('action')=='process_output' and marked==['data'],event
        data=event['data'];assert data.startswith(schema['marker']) and data.count('KFONT')==1
        row=strict_json(data[len(schema['marker']):]);validate(row,schema)
        key=(row['id'],row['phase']);assert key not in records,('duplicate observation',key)
        records[key]=row;phases[row['id']].append(row['phase'])
    expected={(name,phase) for name in schema['ids'] for phase in schema['phases']}
    assert set(records)==expected and len(records)==schema['records']
    assert all(values==schema['phases'] for values in phases.values()),phases
    return [records[key] for key in sorted(records)]
