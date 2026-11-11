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
    assert type(row) is dict
    assert set(row)=={'id','phase','frames','baseline','computed','animationType','currentTime','progress','effectComposite'}
    assert row['id'] in schema['ids'] and row['phase'] in schema['phases']
    assert type(row['animationType']) is str and row['animationType']
    assert row['effectComposite'] in ['replace','add','accumulate']
    assert number(row['currentTime'],True) and number(row['progress'],True)
    for field in ['baseline','computed']:
        assert type(row[field]) is dict and set(row[field])==set(schema['style_properties'])
        assert all(type(value) is str for value in row[field].values())
    assert type(row['frames']) is list
    for frame in row['frames']:
        assert type(frame) is dict
        assert {'offset','computedOffset','easing','composite'} <= set(frame)
        assert number(frame['offset'],True) and number(frame['computedOffset'])
        assert type(frame['easing']) is str
        assert frame['composite'] in ['auto','replace','add','accumulate']
        assert all(type(k) is str and type(v) is str for k,v in frame.items() if k not in ['offset','computedOffset'])


def parse(path):
    schema=strict_json((HERE/'OBSERVATION-SCHEMA.json').read_text())
    records={}
    for line in Path(path).read_text().splitlines():
        event=strict_json(line)
        assert type(event) is dict
        marked=[key for key in ['data','message'] if type(event.get(key)) is str and 'KCUSTOM' in event[key]]
        if not marked:
            continue
        assert event.get('action')=='process_output' and marked==['data'],event
        data=event['data']
        assert data.startswith(schema['marker']) and data.count('KCUSTOM')==1,data
        row=strict_json(data[len(schema['marker']):])
        validate(row,schema)
        key=(row['id'],row['phase'])
        assert key not in records,('duplicate observation',key)
        records[key]=row
    expected={(name,phase) for name in schema['ids'] for phase in schema['phases']}
    assert set(records)==expected and len(records)==schema['records'],('observation inventory',set(records)^expected)
    return [records[key] for key in sorted(records)]
