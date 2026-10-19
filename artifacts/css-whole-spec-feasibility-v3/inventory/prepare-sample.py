from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Anchors(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.lines = text.splitlines(keepends=True)
        self.items = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        ident = dict(attrs).get('id')
        if ident or tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            line, col = self.getpos()
            pos = len(''.join(self.lines[:line - 1]).encode()) + len(self.lines[line - 1][:col].encode())
            self.items.append((ident, tag, pos))


ROWS = [
    ('box.residual', 'snapshot', 'css-official', 'authority-edge', 'CSS theory curator',
     'Box 3 replacement scope', 'Retain CSS2 margin collapsing section 8.3.1 in the selected theory.',
     ['css2-margin-collapsing'], 'explicit retained complement', 'module composition'),
    ('flex.freeze', 'flex', 'resolve-flexible-lengths', 'required-algorithm', 'flex layout UA',
     'one flex line after basis and hypothetical sizing', 'Iterate distribution, clamp violations, and freeze selected items until done.',
     ['flex-basis', 'used-min-max', 'numeric-domain'], 'deterministic within supplied inputs', 'used main sizes'),
    ('break.forced', 'break', 'forced-breaks', 'required-conditional', 'fragmenting UA',
     'applicable break point and matching fragmentation context', 'Honor combined forced break types; later flow position resolves competing page sides.',
     ['break-propagation', 'nested-contexts'], 'ordered resolution', 'fragment placement'),
    ('break.allowed', 'break', 'unforced-breaks', 'constrained-choice', 'fragmenting UA',
     'overflow and current stage of break-rule relaxation', 'Choose allowed breaks; relax rules in prescribed stages and preserve progress constraints.',
     ['break-opportunities', 'fragmentainer-geometry'], 'fragmentation decision with progress', 'fragment placement'),
    ('break.optimize', 'break', 'best-breaks', 'recommendation', 'fragmenting UA',
     'more than one allowed break plan', 'Optimization guidelines do not select one uniquely required break plan.',
     ['break.allowed'], 'possibly competing objectives', 'fragment placement'),
    ('font.choice', 'fonts', 'font-style-matching', 'constrained-choice', 'font matching UA',
     'multiple faces remain after style matching', 'Select one remaining face with consistency across elements in one document.',
     ['available-fonts', 'style-matching'], 'document-consistent policy', 'selected font'),
    ('font.cluster', 'fonts', 'cluster-matching', 'required-conditional', 'font matching UA',
     'base character plus modifiers; variation-selector branch distinguished', 'Attempt required full-sequence fallback before base-character fallback; retain optional non-selector fallback branch.',
     ['unicode-clusters', 'canonical-equivalence', 'font-support', 'installed-fallback'], 'branch-dependent permission', 'selected font and glyph sequence'),
    ('color.missing', 'color', 'interpolation-missing', 'required-algorithm', 'color interpolation consumer',
     'conversion between specified endpoint and interpolation spaces', 'Carry missing analogous components or complete analogous sets through conversion before interpolation.',
     ['color-conversion', 'host-interpolation-space', 'alpha-premultiplication'], 'no arbitrary choice in this step', 'interpolated color components'),
    ('html.style', 'html-style', 'the-style-element', 'required-transition', 'HTML UA',
     'specified parser/connection/children-change triggers', 'Update the associated stylesheet with ordered removal, guards, creation and host lifecycle effects.',
     ['dom-triggers', 'cssom-sheet-lifecycle', 'csp-inline', 'resource-completion'], 'event and host state dependent', 'stylesheet availability'),
    ('html.render', 'html-rendering', 'rendering', 'role-dependent', 'HTML UA',
     'supports-suggested-default-rendering designation', 'Interpret expected rendering as mandatory for the designated conformance role, otherwise as suggestions.',
     ['html-conformance-role', 'ua-stylesheet'], 'role-indexed semantics', 'default rendering'),
]


def main():
    locks = {r['id']: r for r in json.loads((ROOT / 'source-lock.json').read_text())}
    rows = []
    for ident, source, anchor, modality, subject, guard, outcome, deps, choice, phase in ROWS:
        lock = locks[source]
        data = (ROOT / lock['path']).read_bytes()
        items = Anchors(data.decode()).items
        matches = [x for x in items if x[0] == anchor]
        assert len(matches) == 1
        _, tag, start = matches[0]
        end = next((pos for _, t, pos in items if pos > start and t in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')), len(data))
        rows.append(dict(id=ident, source=source, anchor=anchor,
                         source_span=dict(start=start, end=end, sha256=sha(data[start:end])),
                         modality=modality, subject=subject, applicability=guard,
                         quantification='all admitted inputs satisfying the stated applicability; exact domain still requires interpretation',
                         outcome=outcome, dependencies=[dict(id=d, status='open') for d in deps],
                         choice_scope=choice, observation=phase,
                         interpretation='candidate-not-independently-reviewed',
                         source_accounting='selected section only; remaining obligations unclassified',
                         model_coverage='unbound', proof_coverage='unbound', engine_conformance='unbound',
                         semantic_closed=False))
    out = dict(schema_version=1, universe_complete=False, source_accounting_complete=False,
               theory_view='research examples from dated Snapshot plus explicitly pinned drafts; not a reconciled complete theory',
               requirements=rows)
    (ROOT / 'sample-ledger.json').write_text(json.dumps(out, indent=2) + '\n')
    review = {r['id']: {k: r[k] for k in ('source', 'anchor', 'modality', 'applicability', 'choice_scope')} for r in rows}
    (ROOT / 'reviewed-shape.json').write_text(json.dumps(review, indent=2) + '\n')


if __name__ == '__main__':
    main()
