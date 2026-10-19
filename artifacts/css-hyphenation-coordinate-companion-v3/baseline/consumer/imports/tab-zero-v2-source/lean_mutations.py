import json

MUTATIONS=[
 ('zero_identity','if width = 0 then x else legacy width minimum x','if width = 0 then x + minimum else legacy width minimum x',
  'Tab.candidate 0 10 3','3','13'),
 ('glyph_accumulation','pending := s.pending + n,','pending := s.pending,',
  '(Tab.nativeRun .minimum id [.glyph 20] {current := 0}).current','20','0'),
 ('tab_transition','current := policy flushed.current,','current := flushed.current,',
  '(Tab.nativeRun .minimum (fun x => x+10) [.tab] {current := 0}).current','10','0'),
 ('normal_zero_gate','else { s with cursor := s.cursor + 1, trace := s.trace ++ [(1,s.cursor,0)] }',
  'else { s with measured := s.measured + 1, cursor := s.cursor + 1, trace := s.trace ++ [(1,s.cursor,0)] }',
  '(Tab.normalLoop false id [.tab] {measured := 0, offset := 0, origin := 0, cursor := 0}).measured','0','1'),
 ('preferred_metadata','empty := if mode == .preferred then false else flushed.empty,','empty := flushed.empty,',
  'if (Tab.nativeRun .preferred id [.tab] {current := 0}).empty then (1 : Nat) else 0','0','1'),
 ('normal_record','records := s.records ++ [(s.cursor - s.origin,next - s.offset)],','records := s.records,',
  '(Tab.normalLoop true (fun x => x+10) [.tab] {measured := 0, offset := 0, origin := 0, cursor := 0}).records.length','1','0'),
]


def check(base,out,lean,run):
    source=(base/'Tab.lean').read_text();defs=source[:source.index('@[simp] theorem zero_identity')]
    receipt={}
    for name,old,new,expr,expected,changed in MUTATIONS:
        assert source.count(old)==defs.count(old)==1,name
        directory=out/('lean-mutant-'+name);directory.mkdir()
        mutant=directory/'Proof.lean';mutant.write_text(source.replace(old,new))
        proof=run([lean,mutant],directory/'proof.log',allow_failure=True)
        assert proof!=0,name
        assert any(term in (directory/'proof.log').read_text() for term in ['unsolved goals','failed','mismatch']),name
        outputs=[]
        for variant,text in [('reference',defs),('changed',defs.replace(old,new))]:
            f=directory/(variant+'.lean');f.write_text(text.replace('import Std','import Std\nset_option linter.unusedVariables false')+'\nend Tab\ndef main : IO Unit := IO.println ('+expr+')\n')
            run([lean,'--run',f],directory/(variant+'.log'))
            actual=(directory/(variant+'.log')).read_text().strip();outputs.append(actual)
        assert outputs==[expected,changed] and expected!=changed,(name,outputs)
        receipt[name]=dict(proof_exit=proof,reference_exit=0,changed_exit=0,
                           reference=expected,changed=changed,expression=expr)
    return receipt
