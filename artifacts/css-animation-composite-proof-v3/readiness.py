import copy
import hashlib
import json

from oracle import derive, segments, specified


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def property_observations(properties):
    return [[property[0],property[1],property[3]] for property in properties]


class DispatchReadiness:
    def __init__(self):
        self.rows=[]
        self.provider_versions=[]

    def offset_key(self):
        ranged=any(frame['offset'] is not None and frame['offset'][0]!=0 for frame in self.frames)
        if not ranged:return digest(['ordinary',specified(self.frames)])
        active=self.animation and self.env['view']>=0
        geometry=self.env if active else None
        return digest([specified(self.frames),bool(active),geometry])

    def property_key(self):
        return digest([specified(self.frames),[frame['computed'] for frame in self.frames],self.default,self.version,self.target,self.style_on])

    def ready(self):
        return not self.pending and self.offset_basis==self.offset_key() and self.property_basis==self.property_key() and (not self.target or self.base_version==self.version)

    def version_change(self):
        self.version+=1
        self.provider_versions.append(dict(step=self.current_step,version=self.version,base=self.style['base'],scale=self.style['scale'],fail=self.style['fail'],target=self.target,style_available=self.style_on))

    def apply(self,action,row,same):
        op=action['op'];trace=row['trace'];self.current_step=row['step']
        before=False if op=='RESET' else self.ready()
        old_offsets=[] if op=='RESET' else [frame['computed'] for frame in self.frames]
        equal_skip=op=='SET' and not action['error'] and 'compute' not in trace
        if op=='RESET':
            self.frames=[];self.default=action['default'];self.target=action['target'];self.style_on=action['style'];self.animation=action['animation'];self.env=copy.deepcopy(action['env']);self.style=dict(base=action['base'],scale=action['scale'],fail=action['fail']);self.version=0
            self.pending=True;self.offset_basis=self.offset_key();self.property_basis=None;self.base_version=None
            self.provider_versions.append(dict(step=self.current_step,version=0,base=self.style['base'],scale=self.style['scale'],fail=self.style['fail'],target=self.target,style_available=self.style_on))
        elif op in ('INVALIDATE','STYLE'):
            self.style.update(base=action['base'],scale=action['scale'])
            if op=='INVALIDATE':self.target=action['target'];self.style_on=action['style']
            self.version_change();self.pending=True
        elif op=='DEFAULT':
            if self.default!=action['value']:self.pending=True
            self.default=action['value']
        elif op=='CONTEXT':self.env=copy.deepcopy(action['env'])
        self.frames=copy.deepcopy(row['frames'])
        if 'compute' in trace:
            assert op=='SET' and not action['error'] and trace.count('compute')==1
            self.offset_basis=self.offset_key();self.pending=True
        if 'refresh' in trace:
            assert op in ('GET','CONTEXT') and self.animation and self.env['view']>=0
            assert trace.count('refresh')==1
            self.offset_basis=self.offset_key()
            if old_offsets!=[frame['computed'] for frame in self.frames]:self.pending=True
        if self.offset_basis!=self.offset_key():self.pending=True
        updated='update' in trace
        if updated:
            assert trace.count('update')==trace.count('build')==trace.count('base-styles')==1
            assert trace.index('update')<trace.index('build')<trace.index('base-styles')
            if self.target:
                assert trace.count('computed-values')==1 and trace.index('computed-values')<trace.index('base-styles')
                self.base_version=self.version
            self.property_basis=self.property_key()
            self.pending=self.offset_basis!=self.offset_key()
        if op=='SET' and action['error']:
            assert 'compute' not in trace and not updated
        after=self.ready()
        current_checks=None
        if after:
            context=dict(self.env,active=self.animation and self.env['view']>=0)
            current_frames=copy.deepcopy(self.frames)
            offsets=derive(current_frames,context)
            for frame,offset in zip(current_frames,offsets):frame['computed']=offset
            current_properties=segments(current_frames,self.default,self.style) if self.target else []
            current_base=[]
            for pid,name,running,built in current_properties:
                if any(segment[2] is None or segment[3] is None or segment[5]!=0 or segment[6]!=0 for segment in built):current_base.append([pid,name,self.style['base']])
            current_base.sort(key=lambda entry:(entry[0],entry[1]))
            assert same([frame['computed'] for frame in self.frames],offsets),(row['step'],'ready offsets')
            assert same(property_observations(row['properties']),property_observations(current_properties)),(row['step'],'ready properties')
            if self.target:assert same(row['base'],current_base),(row['step'],'ready base')
            current_checks=dict(offsets=True,properties=True,base=True if self.target else 'inactive-target-no-current-base-obligation')
        if equal_skip:
            assert not updated and 'notify' not in trace
            if before:assert after,(row['step'],'ready skip lost readiness')
        record=dict(step=row['step'],op=op,pre_ready=before,post_ready=after,equal_skip=equal_skip,admitted_equal_skip=equal_skip and before,withheld_equal_skip=equal_skip and not before,completed_offset_distribution='compute' in trace,completed_offset_refresh='refresh' in trace,completed_property_base_update=updated,provider_version=self.version,offset_input_key=self.offset_key(),offset_delivery_key=self.offset_basis,property_input_key=self.property_key(),property_delivery_key=self.property_basis,base_delivery_version=self.base_version,pending=self.pending,current_checks=current_checks,trace=trace)
        self.rows.append(record)
        return record


def check_readiness(cases,rows,same):
    monitor=DispatchReadiness();case_receipts=[];start=0
    for case in cases:
        records=[]
        for action,row in zip(case['actions'],rows[start:start+len(case['actions'])]):records.append(monitor.apply(action,row,same))
        admitted=all(not record['withheld_equal_skip'] for record in records)
        case_receipts.append(dict(name=case['name'],start=start,actions=len(records),admitted_equal_step_sequence=admitted,equal_steps=sum(r['equal_skip'] for r in records),ready_prefixes=[r['step'] for r in records if r['post_ready']],withheld_equal_prefixes=[r['step'] for r in records if r['withheld_equal_skip']]))
        if case['name'].startswith('ready-'):
            assert admitted and any(r['admitted_equal_skip'] for r in records),case['name']
        if case['name']=='ready-offset-then-style-delivery':
            assert records[3]['completed_offset_refresh'] and not records[3]['completed_property_base_update'] and not records[3]['post_ready']
            assert records[4]['completed_property_base_update'] and records[4]['post_ready']
        if case['name']=='diagnostic-undelivered-identical-provider':
            assert records[3]['withheld_equal_skip'] and records[6]['admitted_equal_skip']
            native=rows[start:start+len(records)]
            assert native[1]['properties']==native[3]['properties']==native[5]['properties']
            assert native[1]['base']==native[3]['base']==native[5]['base']
        if case['name']=='diagnostic-style-delivery-before-offsets':
            assert records[3]['completed_property_base_update'] and not records[3]['post_ready']
            assert records[4]['withheld_equal_skip'] and records[6]['post_ready'] and records[7]['admitted_equal_skip']
        start+=len(records)
    assert start==len(rows)
    return dict(scope='Raw-provider input versions plus actual completed distribution/refresh/build/base traces certify readiness. Expected current caches are computed only after certification, never used to admit a step. Scheduler delivery and immutable provider snapshots remain external premises.',rows=monitor.rows,provider_versions=monitor.provider_versions,cases=case_receipts,counts=dict(action_rows=len(rows),ready_prefixes=sum(r['post_ready'] for r in monitor.rows),admitted_equal_skips=sum(r['admitted_equal_skip'] for r in monitor.rows),withheld_equal_skips=sum(r['withheld_equal_skip'] for r in monitor.rows),admitted_case_sequences=sum(r['admitted_equal_step_sequence'] for r in case_receipts),admitted_nonvacuous_case_sequences=sum(r['admitted_equal_step_sequence'] and r['equal_steps']>0 for r in case_receipts),no_equal_step_case_sequences=sum(r['equal_steps']==0 for r in case_receipts),case_sequences=len(cases)))
