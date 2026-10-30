import json
from pathlib import Path


def main(request, response):
    directory = Path(__file__).parent
    response.headers.set(b'Content-Type', b'application/json')
    response.headers.set(b'Cache-Control', b'no-store')
    try:
        config = json.loads((directory / 'CONFIG.json').read_bytes())
        assert request.method == 'POST'
        assert request.headers.get(b'Content-Type') == b'application/json'
        assert request.headers.get(b'Origin') == b'http://' + request.headers.get(b'Host', b'')
        body = request.body
        assert 0 < len(body) <= 65536
        payload = json.loads(body)
        assert set(payload) == {'version', 'nonce', 'role', 'page', 'row'}
        assert payload['version'] == 1 and payload['nonce'] == config['nonce']
        assert payload['role'] == config['role'] and payload['page'] == config['page']
        assert payload['row']['kind'] == 'zoom-observation'
        with (directory / 'REQUEST.json').open('xb') as stream:
            stream.write(body)
        return b'{"accepted":true}'
    except Exception as error:
        with (directory / 'ERRORS.jsonl').open('a') as stream:
            stream.write(json.dumps({'error': type(error).__name__}) + '\n')
        response.status = 400
        return b'{"accepted":false}'
