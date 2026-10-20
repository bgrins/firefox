import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

DOCUMENTS = [
    ('fragmentation', 'https://drafts.csswg.org/css-break-3/', 'unforced-breaks'),
    ('html-style', 'https://html.spec.whatwg.org/multipage/semantics.html', 'update-a-style-block'),
    ('font-clusters', 'https://drafts.csswg.org/css-fonts-4/', 'cluster-matching'),
]


def fetch(output):
    output.mkdir(parents=True, exist_ok=False)
    (output / 'sources').mkdir()
    rows = []
    for identity, url, anchor in DOCUMENTS:
        row = dict(id=identity,url=url,anchor=anchor,fetched_utc=datetime.now(timezone.utc).isoformat())
        try:
            request = urllib.request.Request(url,headers={'User-Agent':'CSS-source-ledger-research/1'})
            with urllib.request.urlopen(request,timeout=60) as response:
                data = response.read()
                row.update(final_url=response.url,content_type=response.headers.get('Content-Type'),
                           etag=response.headers.get('ETag'),last_modified=response.headers.get('Last-Modified'))
            data.decode('utf-8',errors='strict')
            path = 'sources/' + identity + '.html'
            (output / path).write_bytes(data)
            row.update(status='acquired',path=path,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        except Exception as error:
            row.update(status='failed',error=str(error))
        rows.append(row)
    (output / 'sources.lock.json').write_text(json.dumps({'format':1,'documents':rows},indent=2)+'\n')
    return all(r['status'] == 'acquired' for r in rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(0 if fetch(parser.parse_args().output) else 1)
