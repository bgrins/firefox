NAMES={1:"extra-root-zoom",2:"dropped-cache-zoom",3:"scaled-publication",4:"default-root-provider",5:"wrong-inherited-base",6:"wrong-document-provider",7:"stale-admitted-refresh",8:"dropped-coefficient",9:"duplicate-coefficient",10:"dropped-inherited-transport"}
def change(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)
def mutate(text,number):
    if number==1:
        text=change(text,"if context.builder.is_root_element {\n                    reference_size\n                } else {", "if context.builder.is_root_element {\n                    reference_size.zoom(context.builder.effective_zoom)\n                } else {")
    elif number==2:
        text=change(text,"let reference_size = if context.builder.is_root_element {\n                    reference_size\n                } else {", "let reference_size = if context.builder.is_root_element || !context.in_media_query {\n                    reference_size\n                } else {")
    elif number==3:
        text=change(text,"new_primary_style\n                        .effective_zoom\n                        .unzoom(new_line_height.px())", "new_line_height.px()")
    elif number==4:
        begin=text.index("LengthUnit::Rlh =>")
        section=text[begin:]
        old="""context
                        .builder
                        .calc_line_height(
                            context.device(),
                            line_height_base,
                            context.style().writing_mode,
                        )"""
        new="""context.device().calc_line_height(context.default_style().get_font(), context.style().writing_mode, None)"""
        section=change(section,old,new);text=text[:begin]+section
    elif number==5:
        text=change(text,"self.get_parent_font(),\n                ComputedValueFlags::DEPENDS_ON_INHERITED_FONT_METRICS,", "self.get_font(),\n                ComputedValueFlags::DEPENDS_ON_INHERITED_FONT_METRICS,")
    elif number in (6,7):
        pass
    elif number==8:
        text=change(text,"(reference_size * length).finite()","(reference_size * if PREPARING.with(|x|x.get()){length}else{1.0}).finite()")
    elif number==9:
        text=change(text,"(reference_size * length).finite()","if PREPARING.with(|x|x.get()){(reference_size * length).finite()}else{((reference_size * length) * length).finite()}")
    elif number==10:
        text=change(text,"self.effective_zoom_for_inheritance.zoom(lh.px())", "lh.px()")
    else: raise ValueError(number)
    return text
