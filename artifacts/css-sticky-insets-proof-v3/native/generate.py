from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
def generate(variant, driver):
    spec=importlib.util.spec_from_file_location('extract',ROOT/'source_extract.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    r={x['name']:x['body'] for x in module.selected(variant)}
    t=(ROOT/'native/prefix.cpp').read_text()
    groups={'DISPLACEMENT_RECORD':['displacement_record'],'RECT_OVERFLOW':['rect_overflows'],'CB_VALUE':['compute_cb_value'],'MARGIN_METHODS':['margin_default','margin_constructor','margin_horizontal','margin_vertical','margin_side','margin_const_side'],'TIMELINE_METHODS':['timeline_earliest','timeline_latest','timeline_displacement'],'WM_METHODS':['wm_vertical','wm_inline_reverse','wm_rtl','wm_block','wm_inline','wm_side'],
      'RECT_METHODS':['union_saturating','union_saturating_edges','rect_union_edges','rect_union','rect_union_assign','rect_deflate','rect_margin','rect_left','rect_right','rect_top','rect_bottom'],
      'FRAME_METHODS':['is_block','nearest_block','get_cb','get_normal'],
      'UNION_METHODS':['union_add','union'],
      'STICKY_METHODS':['nearest_scroll','get_container','side_offset','scroll_size','compute_offsets','limits','position','ignoring','do_position','translation','stuck_y','scroll_ranges','axis_ranges','continuations','update']}
    for key,names in groups.items(): t=t.replace('@@'+key+'@@','\n'.join(r[x] for x in names))
    t=t.replace('@@ABSOLUTE@@','template<class T,class Sub,class Point,class Rect>\n'+r['absolute']+';')
    if '@@' in t:raise RuntimeError('unfilled template')
    return t+'\n'+(ROOT/'native'/driver).read_text()
