import argparse
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
REPO=BASE.parent.parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');parser.add_argument('--source-only',action='store_true')
    args=parser.parse_args()
    paths=json.loads((BASE/'SOURCE-ONLY-v1.json').read_text())
    for name,digest in paths.items():assert sha(BASE/name)==digest,name
    frozen=0
    if not args.source_only:
        entries=json.loads((BASE/'FREEZE-v1.json').read_text())['files']
        for name,digest in entries.items():assert sha(BASE/name)==digest,name
        frozen=len(entries)
        for name,digest in json.loads((BASE/'EXTERNAL-EVIDENCE-v2.json').read_text()).items():
            assert sha(REPO/name)==digest,name
    pins=json.loads((BASE/'REPLAY-INPUTS-v1.json').read_text())
    for name,digest in pins.items():assert sha(BASE/name)==digest,name
    origins=json.loads((BASE/'ORIGINS-v1.json').read_text());live=0
    for entry in origins:
        assert sha(BASE/entry['snapshot'])==entry['sha256'],entry['snapshot']
        if args.live and entry['live']:
            assert sha(REPO/entry['source'])==entry['sha256'],entry['source'];live+=1
    print(json.dumps(dict(status='PASS',frozen_files=frozen,source_only_paths=len(paths),replay_pins=len(pins),live_origins=live)))


if __name__=='__main__':main()
