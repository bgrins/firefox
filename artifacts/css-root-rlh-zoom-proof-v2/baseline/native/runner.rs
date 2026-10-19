fn n(tokens:&[&str],i:usize)->f32{tokens[i].parse().unwrap()}
fn u(tokens:&[&str],i:usize)->u32{tokens[i].parse().unwrap()}
fn make_font(owner:u32,zoom:f32,size:f32,tag:u32,value:f32)->Font {
    if tag!=3 {return font(owner,size*zoom,tag,if tag==0{value*zoom}else{value});}
    let saved=TRACE.with(|x|std::mem::take(&mut *x.borrow_mut()));
    let seed=font(owner,size*zoom,0,0.0);
    let builder=Builder{font:seed.clone(),parent:seed,is_root_element:false,effective_zoom:Zoom(zoom),effective_zoom_for_inheritance:Zoom(zoom),writing_mode:WritingMode{vertical:false},flags:Cell::new(0),owner};
    let device=Device{root_line_height:AtomicU32::new(0),used_root_line_height:AtomicBool::new(false),has_pc:true,root_metrics:16.0,owner};
    let context=Context{builder:&builder,device:&device,default:&builder,in_media_query:false,for_non_inherited_property:true,rule_cache_conditions:RefCell::new(Conditions::default())};
    PREPARING.with(|x|x.set(true));
    let computed=resolve_line_height_length(&context,NoCalcLength{unit:LengthUnit::Em,value}).px();
    PREPARING.with(|x|x.set(false));
    let trace=TRACE.with(|x|std::mem::replace(&mut *x.borrow_mut(),saved));
    PREPARATION.with(|x|x.borrow_mut().push(trace));
    font(owner,size*zoom,0,computed)
}
fn make_builder(owner:u32,zoom:f32,size:f32,tag:u32,value:f32)->Builder {
    Builder{font:make_font(owner,zoom,size,tag,value),parent:make_font(owner+1,1.0,16.0,0,24.0),is_root_element:false,effective_zoom:Zoom(zoom),effective_zoom_for_inheritance:Zoom(zoom),writing_mode:WritingMode{vertical:false},flags:Cell::new(0),owner}
}
fn unit(v:u32)->LengthUnit {match v {0=>LengthUnit::Rlh,1=>LengthUnit::Lh,2=>LengthUnit::Em,3=>LengthUnit::Rem,4=>LengthUnit::Ex,5=>LengthUnit::Rex,6=>LengthUnit::Ch,7=>LengthUnit::Rch,8=>LengthUnit::Cap,9=>LengthUnit::Rcap,10=>LengthUnit::Ic,11=>LengthUnit::Ric,_=>LengthUnit::Px}}
fn main() {
    assert_eq!((std::mem::size_of::<LineHeight>(),std::mem::align_of::<LineHeight>()),(8,4));
    assert_eq!((std::mem::size_of::<NativeFont>(),std::mem::align_of::<NativeFont>()),(20,4));
    assert_eq!((std::mem::size_of::<FontData>(),std::mem::align_of::<FontData>()),(32,4));
    assert_eq!((std::mem::offset_of!(FontData,font),std::mem::offset_of!(FontData,explicit)),(8,28));
    let mut root=make_builder(10010,1.0,16.0,0,20.0);
    root.is_root_element=true;
    let mut version=0u32;
    let mut published_version=None;
    let mut publishes=0u32;
    let mut device=Device{root_line_height:AtomicU32::new(0),used_root_line_height:AtomicBool::new(false),has_pc:true,root_metrics:16.0,owner:10010};
    let foreign=Device{root_line_height:AtomicU32::new(64.0f32.to_bits()),used_root_line_height:AtomicBool::new(false),has_pc:true,root_metrics:31.0,owner:20010};
    for line in io::stdin().lock().lines() {
        let line=line.unwrap(); let t:Vec<&str>=line.split_whitespace().collect();if t.is_empty(){continue;}
        TRACE.with(|x|x.borrow_mut().clear());
        PREPARATION.with(|x|x.borrow_mut().clear());
        match t[0] {
            "ROOT"=>{
                let owner=u(&t,1)*10000+u(&t,2);version=u(&t,3);
                root=make_builder(owner,n(&t,4),n(&t,5),u(&t,6),n(&t,7));root.is_root_element=true;
                device.owner=owner; published_version=None;
                println!("{{\"event\":\"root\",\"version\":{},\"owner\":{},\"cache_bits\":{},\"used\":{}}}",version,owner,device.root_line_height.load(Ordering::Relaxed),device.used_root_line_height.load(Ordering::Relaxed));
            },
            "PUBLISH"=>{
                if MUTANT!=7 || publishes==0 {publish(&device,&root,true);}
                publishes+=1;published_version=Some(version);
                println!("{{\"event\":\"publish\",\"version\":{},\"owner\":{},\"cache_bits\":{},\"used\":{},\"trace\":{:?}}}",version,device.owner,device.root_line_height.load(Ordering::Relaxed),device.used_root_line_height.load(Ordering::Relaxed),TRACE.with(|x|x.borrow().clone()).iter().map(|(a,b,c,d)|[*a,*b,*c,*d]).collect::<Vec<_>>());
            },
            "READ"=>{
                let id=u(&t,1);let role=u(&t,2);let units=u(&t,3);let base=u(&t,4);let coefficient=n(&t,5);
                let owner=u(&t,6);let zoom=n(&t,7);let parent_owner=u(&t,8);let parent_zoom=n(&t,9);
                let mut builder=if role==0 || role==3 {root.clone()}else{make_builder(owner,zoom,n(&t,10),u(&t,11),n(&t,12))};
                builder.parent=make_font(parent_owner,parent_zoom,n(&t,13),u(&t,14),n(&t,15));
                builder.effective_zoom_for_inheritance=Zoom(builder.effective_zoom.0/parent_zoom);
                builder.flags.set(0);
                let default=make_builder(10000,1.0,n(&t,16),u(&t,17),n(&t,18));
                device.has_pc=u(&t,19)!=0;
                if role==2 && units==0 {assert_eq!(published_version,Some(version),"schedule missing admitted refresh");}
                let selected=if MUTANT==6 && role==2 && units==0 {&foreign}else{&device};
                let context=Context{builder:&builder,device:selected,default:&default,in_media_query:role==1 || role==3,for_non_inherited_property:true,rule_cache_conditions:RefCell::new(Conditions::default())};
                let font_base=if base==0{FontBaseSize::CurrentStyle}else{FontBaseSize::InheritedStyle};
                let lh_base=if base==0{LineHeightBase::CurrentStyle}else{LineHeightBase::InheritedStyle};
                let length=NoCalcLength{unit:unit(units),value:coefficient};
                let value=if u(&t,20)==1 {resolve_line_height_length(&context,length)} else {length.to_computed_value_with_base_size(&context,font_base,lh_base)};
                let exposed=value.to_resolved_value(&ResolvedContext{style:&builder});
                let cpp=unsafe{capsule_cssom(value.0,builder.effective_zoom.0)};
                let cond=context.rule_cache_conditions.borrow();
                println!("{{\"event\":\"read\",\"id\":{},\"version\":{},\"owner\":{},\"provider_device\":{},\"scaled_bits\":{},\"exposed_bits\":{},\"cpp_bits\":{},\"cache_bits\":{},\"used\":{},\"flags\":{},\"font_dependency\":{:?},\"lh_dependency\":{:?},\"trace\":{:?}}}",id,version,builder.owner,selected.owner,value.0.to_bits(),exposed.0.to_bits(),cpp.to_bits(),device.root_line_height.load(Ordering::Relaxed),selected.used_root_line_height.load(Ordering::Relaxed),builder.flags.get(),cond.font.map(|v|v.to_bits()).unwrap_or(0),cond.lh.map(|v|v.to_bits()).unwrap_or(0),TRACE.with(|x|x.borrow().clone()).iter().map(|(a,b,c,d)|[*a,*b,*c,*d]).collect::<Vec<_>>());
            },
            "FOREIGN"=>{foreign.root_line_height.store(n(&t,1).to_bits(),Ordering::Relaxed);println!("{{\"event\":\"foreign\",\"cache_bits\":{}}}",device.root_line_height.load(Ordering::Relaxed));},
            _=>panic!("bad protocol")
        }
        eprintln!("{{\"preparation\":{:?}}}",PREPARATION.with(|x|x.borrow().clone()).iter().map(|v|v.iter().map(|(a,b,c,d)|[*a,*b,*c,*d]).collect::<Vec<_>>()).collect::<Vec<_>>());
    }
}
