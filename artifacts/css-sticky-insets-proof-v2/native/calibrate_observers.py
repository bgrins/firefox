from calibrate import raw_axes

def boxes_source(cases):
    out=['import StickyEndpoints','def emitInts (xs : List Int) : IO Unit := IO.println ("[" ++ String.intercalate "," (xs.map toString) ++ "]")','open StickyGeometry StickyConsumers StickyWritingMode StickyNumeric StickyAbsolute',
      'def emit (id : Int) (x y : Raw) (has : Bool) (raw : Nat) : IO Unit := do',
      ' let xl := selectedLimits x has (isFar (selectedEnd raw .x)) false',
      ' let yl := selectedLimits y has (isFar (selectedEnd raw .y)) false',
      ' let rs := rectangles xl yl',
      ' let e := StickyAbsolute.construct rs.1 rs.2 x.normal y.normal',
      ' let a := machineBox e.1; let b := machineBox e.2',
      ' let ref := StickyAbsolute.reference rs.1 rs.2 x.normal y.normal',
      ' let safe := decide (ObserverSafe rs.1 rs.2 x.normal y.normal)',
      ' emitInts ([id,a.left,a.top,a.right,a.bottom,b.left,b.top,b.right,b.bottom,',
      ' ref.1.left,ref.1.top,ref.1.right,ref.1.bottom,ref.2.left,ref.2.top,ref.2.right,ref.2.bottom,if safe then 1 else 0] : List Int)']
    for c in cases:
        x,y=raw_axes(c);mode=c['scroll_mode'] if c['cb_kind']==1 else c['cb_mode']
        out.append(f"#eval emit {c['id']} ({x}) ({y}) {'true' if c['has_offsets'] else 'false'} {mode}")
    return '\n'.join(out)+'\n'

def endpoints_source(rows):
    out=['import StickyEndpoints','def emitInts (xs : List Int) : IO Unit := IO.println ("[" ++ String.intercalate "," (xs.map toString) ++ "]")','open StickyNumeric StickyConsumers StickyRanges StickyEndpoints',
      'def emit (id axis slot : Int) (offset : Int) (d : Displacement) : IO Unit := do',
      ' let e := StickyEndpoints.construct true offset d; let l := StickyEndpoints.construct false offset d',
      ' emitInts ([id,axis,slot,machineEvaluate e,machineEvaluate l,',
      ' StickyEndpoints.reference true offset d,StickyEndpoints.reference false offset d,',
      ' if decide (Safe true offset d) then 1 else 0, if decide (Safe false offset d) then 1 else 0] : List Int)']
    expected=[]
    for r in rows:
        for axis,key in enumerate(['timeline_x','timeline_y']):
            values=r[key]
            if values is None:continue
            shift,sa,sm,ea,em=values[:5]
            for slot,offset in enumerate([ea-1,ea,ea+1,sa-1,sa,sa+1]):
                d=f'⟨0,{shift},⟨{sa},{sm}⟩,⟨{ea},{em}⟩⟩'
                out.append(f"#eval emit {r['id']} {axis} {slot} ({offset}) ({d})")
                pair=values[5+2*slot:7+2*slot]
                expected.append([r['id'],axis,slot,*pair,*pair,1,1])
    return '\n'.join(out)+'\n',expected
