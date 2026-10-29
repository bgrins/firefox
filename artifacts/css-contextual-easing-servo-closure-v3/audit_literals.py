import hashlib
import json
from pathlib import Path
import re
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
support = HERE / 'baseline/support/stylo_atoms-0.22.0'
known = {
    'pref': set(tomllib.loads((HERE / 'baseline/support/stylo_static_prefs-0.22.0/preferences.toml').read_text())),
    'atom': set((support / 'static_atoms.txt').read_text().splitlines()) | set(
        re.findall(r'"([^"\n]*)"', (support / 'predefined_counter_styles.rs').read_text())) | {''},
    'local_name': set((HERE / 'vendor/web_atoms-0.1.3/local_names.txt').read_text().splitlines()) | {''},
}
known['local_name'] |= {name.lower() for name in known['local_name']}
known['namespace_prefix'] = {'', '*', 'html', 'xml', 'xmlns', 'xlink', 'svg', 'mathml'}
known['namespace_url'] = {'', '*', 'http://www.w3.org/1999/xhtml',
    'http://www.w3.org/XML/1998/namespace', 'http://www.w3.org/2000/xmlns/',
    'http://www.w3.org/1999/xlink', 'http://www.w3.org/2000/svg',
    'http://www.w3.org/1998/Math/MathML'}
gecko_pref_sites = {
    ('global_style_data.rs', 'layout.css.stylo-threads'): 'cfg gecko stylo_threads_pref',
    ('queries/feature_expression.rs', 'layout.css.prefers-reduced-transparency.enabled'): 'cfg gecko block in disabled_by_pref',
    ('queries/feature_expression.rs', 'layout.css.inverted-colors.enabled'): 'cfg gecko block in disabled_by_pref',
    ('properties/cascade.rs', 'browser.display.permit_backplate'): 'cfg gecko BackgroundImage match arm',
    ('properties/cascade.rs', 'browser.display.use_document_fonts'): 'cfg gecko prioritize_user_fonts_if_needed',
    ('values/computed/font.rs', 'mathml.font_family_math.enabled'): 'cfg gecko math_enabled',
    ('stylesheets/supports_rule.rs', 'layout.css.anchor-positioning.follows-transforms.enabled'): 'cfg gecko NamedFeature::eval',
    ('values/specified/text.rs', 'layout.css.control-characters.visible'): 'cfg gecko Default for MozControlCharacterVisibility',
}
pattern = re.compile(r'\b(pref|atom|local_name|namespace_prefix|namespace_url)!\s*\(\s*"([^"\n]*)"')
sources = []
for role in ('baseline', 'candidate'):
    for path in sorted((HERE / role).rglob('*.rs')):
        relative = path.relative_to(HERE / role).as_posix()
        if not relative.startswith('support/'):
            sources.append((role + '/' + relative, relative, path))
for path in sorted((ROOT / 'artifacts/css-contextual-easing-servo-compile-runtime-2/target/debug/build').glob('style-*/out/*.rs')):
    sources.append(('prior-generated/' + path.name, path.name, path))

records = []
generated = []
for name, relative, path in sources:
    if name.startswith('prior-generated/'):
        generated.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})
    short = relative.removeprefix('servo/components/style/')
    for match in pattern.finditer(path.read_text()):
        kind, key = match.groups()
        status = 'available'
        if key not in known[kind]:
            if '${' in key and '.mako.rs' in relative:
                status = 'template placeholder; actual generated properties scanned separately'
            elif relative.startswith('servo/components/style/gecko/'):
                status = 'cfg gecko module'
            elif kind == 'pref' and (short, key) in gecko_pref_sites:
                status = gecko_pref_sites[short, key]
            elif kind == 'atom' and short == 'style_adjuster.rs':
                status = 'cfg gecko is_topmost_svg_svg_element or is_effective_display_none_for_display_contents'
            elif kind == 'atom' and short == 'queries/feature_expression.rs' and key in ('prefers-reduced-transparency', 'inverted-colors'):
                status = 'cfg gecko block in disabled_by_pref'
            elif kind == 'atom' and short == 'values/computed/font.rs' and key == '-moz-bullet-font':
                status = 'cfg gecko FontFamily::moz_bullet'
            else:
                raise AssertionError((name, kind, key))
        records.append({'source': name, 'macro': kind, 'key': key, 'status': status})

assert generated
result = {'method': 'Lexical quoted literal inventory with manually reviewed Gecko cfg exclusions; not a replacement for compiler checking.',
          'unique_keys': {kind: len({r['key'] for r in records if r['macro'] == kind}) for kind in known},
          'unresolved_literals': 0, 'generated_properties': generated, 'records': records}
(HERE / 'LITERAL-AUDIT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({key: value for key, value in result.items() if key != 'records'}, sort_keys=True))
