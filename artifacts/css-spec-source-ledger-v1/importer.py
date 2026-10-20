import argparse
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urldefrag

VERSION = 1
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode() + b'\n'


class SourceNodes(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0] + [m.end() for m in re.finditer('\n', text)]
        self.events = []

    def position(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def emit(self, kind, raw, **fields):
        start = self.position()
        if self.text[start:start + len(raw)] != raw:
            raise ValueError('callback/source mismatch at ' + str(start))
        self.events.append(dict(start=start, end=start + len(raw), kind=kind, **fields))

    def handle_starttag(self, tag, attrs):
        self.emit('start_tag', self.get_starttag_text(), tag=tag, attrs=attrs, void=tag in VOID)

    def handle_startendtag(self, tag, attrs):
        self.emit('empty_tag', self.get_starttag_text(), tag=tag, attrs=attrs, void=True)

    def handle_endtag(self, tag):
        start = self.position()
        end = self.text.find('>', start)
        if end < 0:
            raise ValueError('unterminated callback end tag')
        self.emit('end_tag', self.text[start:end + 1], tag=tag)

    def handle_data(self, data):
        if data:
            self.emit('text', data)

    def handle_comment(self, data):
        start = self.position()
        prefix = '<!--' + data
        if not self.text.startswith(prefix, start):
            raise ValueError('comment callback mismatch')
        match = re.match(r'--\s*>', self.text[start + len(prefix):])
        if match:
            self.emit('comment', prefix + match.group())

    def handle_decl(self, decl):
        self.emit('declaration', '<!' + decl + '>')

    def handle_pi(self, data):
        self.emit('processing_instruction', '<?' + data + '>')

    def handle_entityref(self, name):
        raw = '&' + name
        if self.text.startswith(raw + ';', self.position()):
            raw += ';'
        self.emit('entity_reference', raw)

    def handle_charref(self, name):
        raw = '&#' + name
        if self.text.startswith(raw + ';', self.position()):
            raw += ';'
        self.emit('character_reference', raw)

    def unknown_decl(self, data):
        pass


def annotation(event, text):
    tag = event.get('tag', '')
    attrs = dict(event.get('attrs', []))
    classes = set((attrs.get('class') or '').split())
    kinds = []
    if re.fullmatch(r'h[1-6]', tag):
        kinds.append('heading')
    if tag in {'p', 'dt', 'dd', 'li'} or event['kind'] == 'text' and text.strip():
        kinds.append('prose')
    if tag == 'ol' or 'algorithm' in classes or 'data-algorithm' in attrs:
        kinds.append('algorithm-candidate')
    if tag in {'table', 'thead', 'tbody', 'tr', 'td', 'th', 'caption'}:
        kinds.append('table')
    if 'idl' in classes or 'idl-code' in classes:
        kinds.append('idl-candidate')
    if tag in {'figure', 'figcaption', 'img', 'svg'}:
        kinds.append('figure')
    if tag in {'script', 'style', 'meta', 'link', 'nav'}:
        kinds.append('document-support')
    informative = bool(classes & {'note', 'example', 'informative', 'non-normative'})
    return kinds or ['unclassified'], 'informative-candidate' if informative else 'unclassified'


def inventory(document, raw):
    if digest(raw) != document['sha256'] or len(raw) != document['bytes']:
        raise ValueError('stale source: ' + document['id'])
    text = raw.decode('utf-8', errors='strict')
    byte_at = [0]
    for c in text:
        byte_at.append(byte_at[-1] + len(c.encode('utf-8')))
    parser = SourceNodes(text)
    parser.feed(text)
    parser.close()
    events = []
    cursor = 0
    for event in parser.events:
        if event['start'] < cursor:
            raise ValueError('overlapping callbacks')
        if cursor < event['start']:
            events.append(dict(start=cursor, end=event['start'], kind='unclassified_gap'))
        events.append(event)
        cursor = event['end']
    if cursor < len(text):
        events.append(dict(start=cursor, end=len(text), kind='unclassified_gap'))
    units, anchors, headings, links = [], {}, [], set()
    for i, event in enumerate(events):
        a, b = event.pop('start'), event.pop('end')
        categories, disposition = annotation(event, text[a:b])
        unit = dict(identity=f"{document['id']}:{document['sha256']}:{i}",
                    start=byte_at[a], end=byte_at[b], sha256=digest(raw[byte_at[a]:byte_at[b]]),
                    categories=categories, disposition=disposition, **event)
        units.append(unit)
        if event['kind'] in {'start_tag', 'empty_tag'}:
            attrs = dict(event['attrs'])
            if attrs.get('id'):
                anchors.setdefault(attrs['id'], []).append(i)
            if 'heading' in categories:
                headings.append((i, int(event['tag'][1])))
            if attrs.get('href'):
                links.add(urljoin(document['final_url'], attrs['href']))
    target = anchors.get(document['anchor'], [])
    candidate = None
    if len(target) == 1:
        prior = [(i, rank) for i, rank in headings if i <= target[0]]
        start, rank = prior[-1] if prior else (0, 0)
        end = next((i for i, r in headings if i > start and r <= rank), len(units)) if rank else len(units)
        candidate = dict(anchor=document['anchor'], anchor_unit=target[0], first_unit=start, after_unit=end,
                         start=units[start]['start'], end=units[end - 1]['end'],
                         selection='nearest preceding heading through next same/higher rank; proposed context only',
                         interpretation='proposed; no normative requirements extracted')
    if candidate:
        references = {}
        for unit in units[candidate['first_unit']:candidate['after_unit']]:
            attrs = dict(unit.get('attrs', []))
            if unit['kind'] not in {'start_tag', 'empty_tag'} or not attrs.get('href'):
                continue
            link = urljoin(document['final_url'], attrs['href'])
            base, fragment = urldefrag(link)
            local = base == urldefrag(document['final_url'])[0]
            owners = anchors.get(fragment, []) if local else []
            in_scope = any(candidate['first_unit'] <= i < candidate['after_unit'] for i in owners)
            references[link] = dict(url=link, disposition='inside-candidate' if in_scope else
                                    'same-document-outside-candidate' if owners else 'unresolved-or-external',
                                    interpretation='dependency relevance unreviewed')
        candidate['references'] = [references[k] for k in sorted(references)]
    frontier = []
    if len(target) != 1:
        frontier.append(dict(kind='target-anchor', anchor=document['anchor'], occurrences=len(target)))
    for name, indices in anchors.items():
        if len(indices) > 1:
            frontier.append(dict(kind='duplicate-source-id', anchor=name, units=indices))
    for link in sorted(links):
        base, fragment = urldefrag(link)
        if base == urldefrag(document['final_url'])[0] and fragment:
            if fragment not in anchors:
                frontier.append(dict(kind='unresolved-local-link', url=link))
        elif base != urldefrag(document['final_url'])[0]:
            frontier.append(dict(kind='external-reference-unacquired', url=link))
    result = dict(format=VERSION, document=document['id'], source_sha256=document['sha256'],
                  bytes=len(raw), units=units, anchors=anchors, candidate=candidate, frontier=frontier)
    validate(document, raw, result)
    return result


def validate(document, raw, ledger):
    if digest(raw) != document['sha256'] or len(raw) != document['bytes']:
        raise ValueError('stale source')
    if ledger['source_sha256'] != document['sha256'] or ledger['document'] != document['id'] or ledger['bytes'] != len(raw):
        raise ValueError('wrong source binding')
    cursor, identities = 0, set()
    for i, unit in enumerate(ledger['units']):
        identity = unit['identity']
        if identity in identities:
            raise ValueError('duplicate identity')
        identities.add(identity)
        if identity != f"{document['id']}:{document['sha256']}:{i}":
            raise ValueError('wrong identity')
        if unit['start'] != cursor or not cursor < unit['end'] <= len(raw):
            raise ValueError('missing/overlapping unit')
        data = raw[cursor:unit['end']]
        data.decode('utf-8', errors='strict')
        if digest(data) != unit['sha256']:
            raise ValueError('changed unit bytes')
        cursor = unit['end']
    if cursor != len(raw):
        raise ValueError('unaccounted source suffix')


def run(lock_path, output):
    lock = json.loads(lock_path.read_text())
    ids = [d['id'] for d in lock['documents']]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate document identity')
    results = []
    for document in lock['documents']:
        if document['status'] != 'acquired':
            results.append(dict(document=document['id'], status='acquisition-failed', detail=document))
            continue
        path = (lock_path.parent / document['path']).resolve()
        if not path.is_relative_to(lock_path.parent.resolve()):
            raise ValueError('source path escape')
        data = path.read_bytes()
        result = inventory(document, data)
        results.append(result)
    output.mkdir(parents=True, exist_ok=False)
    summary = []
    for result in results:
        name = result['document']
        (output / (name + '.json.gz')).write_bytes(gzip.compress(canonical(result), mtime=0))
        summary.append({k:v for k,v in result.items() if k not in {'units','anchors','frontier'}} | {
            'unit_count':len(result.get('units', [])), 'anchor_count':len(result.get('anchors', {})),
            'frontier_count':len(result.get('frontier', []))})
    (output / 'SUMMARY.json').write_bytes(canonical(summary))
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--lock', type=Path, default=Path(__file__).with_name('sources.lock.json'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    summary = run(a.lock, a.output)
    print(json.dumps([{k:v for k,v in row.items() if k != 'candidate'} for row in summary], indent=2))
