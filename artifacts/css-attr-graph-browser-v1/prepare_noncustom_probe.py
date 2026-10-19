import json
from pathlib import Path

here=Path(__file__).resolve().parent
root=here.parents[1]
cases=[]
def add(name,decl,attrs,length,font,line):
 cases.append({'name':name,'declarations':decl,'attributes':attrs,'expected':{'--edge-length':length,'font-size':font,'line-height':line,'width':length}})
add('An attr-only font-size declaration participates in a registered length cycle','--edge-length:1em;font-size:attr(a type(<length>),5px)',{'a':'var(--edge-length)'},'11px','23px','31px')
add('A lexical var does not change the font-size attribute cycle','--zero:0px;--edge-length:1em;font-size:calc(var(--zero) + attr(a type(<length>),5px))',{'a':'var(--edge-length)'},'11px','23px','31px')
add('An attr-only line-height declaration participates in a registered length cycle','--edge-length:1lh;line-height:attr(a type(<length>),5px)',{'a':'var(--edge-length)'},'11px','23px','31px')
add('A lexical var does not change the line-height attribute cycle','--zero:0px;--edge-length:1lh;line-height:calc(var(--zero) + attr(a type(<length>),5px))',{'a':'var(--edge-length)'},'11px','23px','31px')
add('An attr-only font-size declaration follows a used attribute fallback','--edge-length:1em;font-size:attr(missing type(<length>),attr(a type(<length>),5px))',{'a':'var(--edge-length)'},'11px','23px','31px')
add('An unused attribute fallback does not create a font-size cycle','--edge-length:1em;font-size:attr(good type(<length>),attr(a type(<length>),5px))',{'good':'13px','a':'var(--edge-length)'},'13px','13px','31px')
add('A literal attribute value does not create a font-size cycle','--edge-length:1em;font-size:attr(a type(<length>),5px)',{'a':'13px'},'13px','13px','31px')
add('A missing attribute uses the literal font-size fallback','--edge-length:1em;font-size:attr(a type(<length>),5px)',{},'5px','5px','31px')
add('A custom property without relative units has no font-size back edge','--edge-length:13px;font-size:attr(a type(<length>),5px)',{'a':'var(--edge-length)'},'13px','13px','31px')
add('A custom property without relative units has no line-height back edge','--edge-length:13px;line-height:attr(a type(<length>),5px)',{'a':'var(--edge-length)'},'13px','23px','13px')
html='''<!doctype html>
<meta charset="utf-8">
<title>Attribute dependencies in font-size and line-height cycles</title>
<link rel="help" href="https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles">
<link rel="help" href="https://drafts.csswg.org/css-values-5/#attr-substitution">
<script src="/resources/testharness.js"></script>
<script src="/resources/testharnessreport.js"></script>
<body>
<script>
CSS.registerProperty({name: "--edge-length", syntax: "<length>", inherits: false,
                      initialValue: "11px"});
const cases = '''+json.dumps(cases,indent=2)+''';
for (const item of cases) {
  test(t => {
    const parent = document.createElement("div");
    parent.style.cssText = "font-size: 23px; line-height: 31px";
    const target = document.createElement("div");
    target.style.cssText = "width: var(--edge-length); " + item.declarations;
    for (const [name, value] of Object.entries(item.attributes)) {
      target.setAttribute(name, value);
    }
    parent.append(target);
    document.body.append(parent);
    t.add_cleanup(() => parent.remove());
    const computed = getComputedStyle(target);
    for (const [property, expected] of Object.entries(item.expected)) {
      assert_equals(computed.getPropertyValue(property).trim(), expected, property);
    }
  }, item.name);
}
</script>
'''
path=root/'testing/web-platform/tests/css/css-values/attr-noncustom-dependency-cycles.html'
assert not path.exists()
path.write_text(html)
(here/'noncustom-cases-v1.json').write_text(json.dumps(cases,indent=2)+'\n')
