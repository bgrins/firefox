import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

HERE=Path(__file__).resolve().parent
URLS={
    'css-animations-2':'https://drafts.csswg.org/css-animations-2/',
    'web-animations-1':'https://drafts.csswg.org/web-animations-1/',
    'css-variables-1':'https://drafts.csswg.org/css-variables-1/',
    'css-properties-values-api-1':'https://drafts.css-houdini.org/css-properties-values-api-1/',
}


def main():
    primary=HERE/'primary'
    primary.mkdir(exist_ok=True)
    receipts={}
    for name,url in URLS.items():
        with urllib.request.urlopen(url,timeout=60) as response:
            data=response.read()
            receipts[name]={'requested':url,'final_url':response.url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        (primary/(name+'.html')).write_bytes(data)
    (HERE/'PRIMARY.json').write_text(json.dumps(receipts,indent=2)+'\n')


if __name__=='__main__':
    main()
