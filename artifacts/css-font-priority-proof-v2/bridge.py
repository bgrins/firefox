from pathlib import Path
from support_b import bridge as frozen

BASE=Path(__file__).resolve().parent
original_text=frozen.text


def text(path,variant='original'):
    candidate=BASE/'candidate'/path
    if variant in ('A','AB') and candidate.exists():return candidate.read_text()
    return original_text(path,variant)


frozen.text=text
generate=frozen.generate
manifest=frozen.manifest
block=frozen.block
ITEMS=frozen.ITEMS
