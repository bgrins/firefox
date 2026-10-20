from oracle import union,deflate,AUTO

def raw_axes(c):
    border=union([c['border']]+([c['continuation_border']] if c['extra'] else []))
    margin=union([c['margin']]+([c['continuation_margin']] if c['extra'] else []))
    contain=c['containing'][:]
    if c['cb_kind']==1:
        contain=deflate(c['overflow'],c['padding'])
        contain[0]+=c['transform'][0];contain[1]+=c['transform'][1]
    size=c['fixed_size'] if c['viewport'] else c['size']
    result=[]
    for j in [0,1]:
        near,far=(c['offsets'][3],c['offsets'][1]) if j==0 else (c['offsets'][0],c['offsets'][2])
        opt=lambda x:'none' if x==AUTO else '(some ('+str(x)+'))'
        n=c['normal'][j] if c['has_normal'] else c['position'][j]
        items=[f'⟨{border[j]},{border[j+2]}⟩',f'⟨{margin[j]},{margin[j+2]}⟩',f'⟨{contain[j]},{contain[j+2]}⟩',
               str(c['position'][j]),str(n),str(size[j]),str(c['padding'][3 if j==0 else 0]),
               str(c['parent_offset'][j]),str(c['scroll'][j]),f'⟨{opt(near)},{opt(far)}⟩']
        result.append('⟨'+','.join(items)+'⟩')
    return result

def lean_source(cases):
    out=['import StickyPipeline','open StickyGeometry StickyConsumers StickyWritingMode StickyNumeric',
      'def run (id : Int) (g : Raw) (has : Bool) (raw : Nat) (axis : Axis) : IO Unit := do',
      ' let ending := isFar (selectedEnd raw axis)',
      ' let source := selectedLimits g has ending false',
      ' let reference := specifiedLimits g has ending false',
      ' IO.println (repr ([id, position g.normal source, StickyPipeline.geometricChoice g.normal reference,',
      ' source.stickNear,source.stickFar,source.containNear,source.containFar] : List Int))']
    for c in cases:
        raw=c['scroll_mode'] if c['cb_kind']==1 else c['cb_mode']
        for axis,g in zip(['x','y'],raw_axes(c)):
            out.append(f"#eval run {c['id']} ({g}) {'true' if c['has_offsets'] else 'false'} {raw} .{axis}")
    return '\n'.join(out)+'\n'
