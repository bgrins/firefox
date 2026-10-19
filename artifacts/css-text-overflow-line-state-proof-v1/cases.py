from copy import deepcopy


def frame(start, size, role=1, parent=-1, visible=True, nonsuppressed=True,
          overflow=None, advances=None):
    if advances is None:
        advances = [20] * (size // 20) + ([size % 20] if size % 20 else []) if role == 1 else []
    assert role != 1 or sum(advances) == size
    return dict(start=start, size=size, role=role, parent=parent, visible=visible,
                nonsuppressed=nonsuppressed, overflow=overflow or [start, start+size],
                advances=advances)


def line(frames, overflow=None, floats=None, clamp=None):
    return dict(frames=frames, overflow=overflow or
                [min((f["overflow"][0] for f in frames), default=0),
                 max((f["overflow"][1] for f in frames), default=0)],
                floats=floats, clamp=clamp)


def style(kind=2, width=40, length=2):
    return dict(kind=kind, width=width, length=length)


def cases():
    end_clip = line([frame(0,80,2),frame(80,80)])
    start_clip = line([frame(-80,100),frame(20,80,2)])
    ordinary = line([frame(-60,220)])
    end_only = line([frame(0,160)])
    start_only = line([frame(-60,160)])
    quiet = line([frame(0,60)])
    patterns = [
        ("end-clipped-ordinary",[end_clip,end_only]),
        ("start-clipped-ordinary",[start_clip,start_only]),
        ("reversed",[ordinary,end_clip,start_clip]),
        ("quiet-gap",[end_clip,quiet,end_only]),
        ("repeat",[end_clip,end_only,end_clip,end_only]),
        ("both",[ordinary]),
    ]
    profiles = [
        ("end",[style(0,0,0),style()]),
        ("start",[style(),style(0,0,0)]),
        ("both",[style(2,20,1),style()]),
    ]
    rows=[]
    def add(name,lines,styles=None,**kwargs):
        c=dict(name=name,lines=deepcopy(lines),styles=deepcopy(styles or profiles[2][1]),
               ltr=True,start=0,width=100,seed=False,ellipsisWidth=30,
               ellipsisFailure=False,scroll=None,snap=False,units=1,domain="ordinary")
        c.update(kwargs);c["id"]=len(rows);rows.append(c)
    for pname,pstyles in profiles:
        for name,lines in patterns:
            for ltr in [True,False]:
                for seed in [False,True]:
                    add(f"{pname}/{name}/{'ltr' if ltr else 'rtl'}/{'seeded' if seed else 'cold'}",lines,pstyles,ltr=ltr,seed=seed)
    extra = [
        ("atomic-overflow",line([frame(-20,140,2)])),
        ("br-placeholder",line([frame(-20,140,3),frame(-20,140,4)])),
        ("hidden-text",line([frame(-20,140,visible=False)])),
        ("suppressed-text",line([frame(-20,140,nonsuppressed=False)])),
        ("hidden-parent-visible-child",line([frame(-20,140,0,visible=False),frame(-20,140,parent=0)])),
        ("atomic-child-not-traversed",line([frame(0,80,2),frame(-20,140,parent=0),frame(100,40,3)],overflow=[-20,140])),
        ("nested",line([frame(-40,180,0),frame(-40,40,parent=0),frame(0,80,2,parent=0),frame(80,60,parent=0)])),
        ("cluster-unequal",line([frame(-10,130,advances=[10,20,30,40,30])])),
        ("cluster-too-large",line([frame(0,160,advances=[160])])),
        ("zero-text",line([frame(-20,0),frame(140,0)])),
        ("overflow-within-line",line([frame(0,80,overflow=[-10,110])],overflow=[-10,110])),
        ("float-both",line([frame(-20,140)],floats=[10,90])),
        ("float-start",line([frame(-20,140)],floats=[20,100])),
        ("float-end",line([frame(-20,140)],floats=[0,80])),
    ]
    for name,ln in extra:
        for ltr in [True,False]:
            add(name+('/ltr' if ltr else '/rtl'),[end_clip,ln,ordinary],ltr=ltr)
    for snap in [False,True]:
        for pos in [0,50,100]:
            add(f"scroll/{snap}/{pos}",[ordinary,end_clip,ordinary],scroll=[pos,0,100],snap=snap,units=2)
    for ltr in [True,False]:
        for widths in [(80,80),(0,40),(40,0),(0,0),(120,40),(20,120)]:
            add(f"widths/{ltr}/{widths}",[ordinary,end_clip,start_clip,ordinary],
                [style(2,widths[0],bool(widths[0])),style(2,widths[1],bool(widths[1]))],ltr=ltr)
        for failure in [False,True]:
            add(f"ellipsis/{ltr}/{failure}",[end_clip,ordinary,quiet,ordinary],
                [style(1,0,0),style(1,0,0)],ltr=ltr,ellipsisFailure=failure)
        add(f"clip-fast-return/{ltr}",[ordinary,quiet],[style(0,0,0),style(0,0,0)],ltr=ltr,domain="fast-return")
        for ck,cw,cl in [(2,30,1),(1,0,0),(0,0,0),(2,0,0)]:
            marked=deepcopy(end_only);marked["clamp"]=[ck,cw,cl]
            add(f"clamp-completion/{ltr}/{ck}/{cw}",[end_clip,marked,end_only],
                profiles[0][1],ltr=ltr,domain="clamp-diagnostic")
        marked=line([frame(0,100,2),frame(100,60)],clamp=[2,30,1])
        add(f"clamp-no-marker-return/{ltr}",[end_clip,marked,end_only],profiles[0][1],ltr=ltr,domain="clamp-diagnostic")
    refinement=line([frame(-20,20,3),frame(0,80,2),frame(80,80)])
    for ltr in [True,False]:
        for seed in [False,True]:
            add(f"clipped-width-survives-guess-refinement/{ltr}/{seed}",
                [refinement,end_only],[style(2,0,0),style()],ltr=ltr,seed=seed)
    return rows


def encode(rows):
    out=[str(len(rows))]
    for c in rows:
        fields=[c["id"],len(c["lines"]),c["ltr"],c["start"],c["width"],c["seed"]]
        for s in c["styles"]:fields += [s["kind"],s["width"],s["length"]]
        fields += [c["ellipsisWidth"],c["ellipsisFailure"],c["scroll"] is not None,
                   *(c["scroll"] or [0,0,100]),c["snap"],c["units"]]
        out.append(" ".join(str(int(x)) for x in fields))
        for ln in c["lines"]:
            fields=[*(ln["clamp"] or [-1,0,0]),ln["floats"] is not None,
                    *(ln["floats"] or [0,100]),*ln["overflow"],len(ln["frames"])]
            out.append(" ".join(str(int(x)) for x in fields))
            for f in ln["frames"]:
                fields=[f["parent"],f["role"],f["visible"],f["nonsuppressed"],f["start"],f["size"],*f["overflow"],len(f["advances"]),*f["advances"]]
                out.append(" ".join(str(int(x)) for x in fields))
    return "\n".join(out)+"\n"
