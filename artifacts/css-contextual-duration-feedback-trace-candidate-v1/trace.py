import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARSER = ROOT / 'artifacts/css-contextual-duration-pending-restyle-trace-parser-v1/trace.py'
spec = importlib.util.spec_from_file_location('sealed_duration_trace_parser', PARSER)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
parse = parser.parse


def capture(phase):
    paths = {'raw':phase / 'raw.jsonl', 'log':phase / 'wpt.log'}
    pins, texts = {}, {}
    for kind, path in paths.items():
        assert path.is_file() and not path.is_symlink()
        body = path.read_bytes()
        pins[kind] = {'sha256':hashlib.sha256(body).hexdigest(), 'bytes':len(body)}
        texts[kind] = body.decode()
    primary = 'raw' if parser.PREFIX in texts['raw'] else 'log'
    result = parse(texts[primary])
    result.update(source_files=pins, primary_stream=primary, streams_not_merged_or_deduplicated=True,
                  parser_sha256=hashlib.sha256(PARSER.read_bytes()).hexdigest(), numeric_or_convergence_oracle=False)
    return result
