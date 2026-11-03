import builtins
import copy
import hashlib
import importlib.machinery
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from contextlib import contextmanager


class Rejected(RuntimeError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(body):
    return hashlib.sha256(body).hexdigest()


class Session:
    active_session = None

    def __init__(self, root, functions, scope, allowed_roots, forbidden=()):
        self.root = Path(root).resolve()
        self.functions = copy.deepcopy(functions)
        self.scope = scope
        self.allowed = tuple(str(Path(p).resolve()) for p in allowed_roots)
        self.forbidden = tuple(str(Path(p).resolve()) for p in forbidden)
        self.table = {}
        self.frames = []
        self.internal = 0
        self.original = {}
        self.thread = threading.get_ident()
        self.calls = {}
        self.hits = {}
        self.active = False
        self.executing = set()

    @contextmanager
    def trusted(self):
        self.internal += 1
        try:
            yield
        finally:
            self.internal -= 1

    def path(self, path):
        if isinstance(path, int):
            raise Rejected('file-descriptor I/O is outside saved replay')
        result = os.path.abspath(os.fspath(path))
        if any(result == p or result.startswith(p + os.sep) for p in self.forbidden):
            raise Rejected('forbidden live path: ' + result)
        if not any(result == p or result.startswith(p + os.sep) for p in self.allowed):
            raise Rejected('path outside saved roots: ' + result)
        if self.active:
            with self.trusted():
                resolved = str(self.original[(Path, 'resolve')](Path(result)))
            if not any(resolved == p or resolved.startswith(p + os.sep) for p in self.allowed):
                raise Rejected('resolved path outside saved roots: ' + resolved)
            if any(resolved == p or resolved.startswith(p + os.sep) for p in self.forbidden):
                raise Rejected('resolved forbidden live path: ' + resolved)
        return result

    def add(self, operation, value):
        key = encoded(operation)
        for frame in self.frames:
            if key in frame and frame[key][1] != value:
                raise Rejected('input changed during saved replay: ' + key)
            frame[key] = (operation, copy.deepcopy(value))

    def fingerprint(self, value):
        if isinstance(value, bytes):
            return ['bytes', len(value), digest(value)]
        if isinstance(value, os.stat_result):
            return ['stat', list(value), value.st_atime_ns, value.st_mtime_ns, value.st_ctime_ns]
        if isinstance(value, Path):
            return ['path', str(value)]
        return ['value', value]

    def perform(self, kind, path, args=(), kwargs=None):
        path = self.path(path)
        kwargs = kwargs or {}
        operation = [kind, path, list(args), kwargs]
        try:
            with self.trusted():
                if kind.startswith('path:'):
                    value = self.original[(Path, kind[5:])](Path(path), *args, **kwargs)
                    if kind[5:] in ('glob', 'rglob', 'iterdir'):
                        value = list(value)
                elif kind.startswith('os:'):
                    value = self.original[(os, kind[3:])](path, *args, **kwargs)
                else:
                    raise Rejected('unknown operation')
            if kind in ('path:glob', 'path:rglob', 'path:iterdir'):
                observed = ['paths', [str(p) for p in value]]
            else:
                observed = self.fingerprint(value)
        except OSError as error:
            self.add(operation, ['error', type(error).__name__, error.errno])
            raise
        self.add(operation, observed)
        if kind in ('path:read_bytes', 'path:glob', 'path:rglob', 'path:iterdir', 'os:listdir'):
            self.perform('path:lstat', path)
            if kind == 'path:read_bytes':
                self.perform('path:stat', path)
            if kind in ('path:glob', 'path:rglob', 'path:iterdir'):
                for entry in value:
                    self.perform('path:lstat', entry)
        return value

    def validate(self, ledger):
        probe = {}
        self.frames.append(probe)
        try:
            for operation, expected in ledger.values():
                kind, path, args, kwargs = operation
                try:
                    self.perform(kind, path, args, kwargs)
                except OSError:
                    pass
                key = encoded(operation)
                if probe.get(key, (None, None))[1] != expected:
                    raise Rejected('changed consumed input: ' + key)
            if probe != ledger:
                raise Rejected('dependency facts changed')
        finally:
            self.frames.pop()

    def call(self, identity, binding, args, kwargs, function, seed=None):
        if threading.get_ident() != self.thread:
            raise Rejected('saved replay is single-threaded')
        key = encoded([self.scope, str(self.root), identity, binding, args, kwargs])
        if key in self.executing:
            raise Rejected('recursive in-progress cache key')
        if key in self.table:
            ledger, result = self.table[key]
            try:
                if seed:
                    self.validate(seed)
                self.validate(ledger)
            except BaseException:
                del self.table[key]
                raise
            for operation, value in ledger.values():
                self.add(operation, value)
            self.hits[identity] = self.hits.get(identity, 0) + 1
            return copy.deepcopy(result)
        frame = {}
        self.frames.append(frame)
        self.executing.add(key)
        self.calls[identity] = self.calls.get(identity, 0) + 1
        try:
            if seed:
                self.validate(seed)
            result = function(*copy.deepcopy(args), **copy.deepcopy(kwargs))
            encoded(result)
            if key != encoded([self.scope, str(self.root), identity, binding, args, kwargs]):
                raise Rejected('mutable validation inputs changed during evaluation')
            self.validate(frame)
            self.table[key] = (copy.deepcopy(frame), copy.deepcopy(result))
            return copy.deepcopy(result)
        finally:
            self.executing.remove(key)
            self.frames.pop()

    def wrap_module(self, module, import_ledger):
        path = self.path(module.__file__)
        relative = os.path.relpath(path, self.root)
        record = self.functions.get(relative)
        if record is None:
            return
        body = self.perform('path:read_bytes', path)
        if digest(body) != record['sha256']:
            raise Rejected('changed cached function code')
        if record['function'] != 'validate_refresh':
            raise Rejected('function is not eligible')
        function = getattr(module, record['function'])
        bindings_path = self.root / record['bindings_path']

        def wrapped(*args, **kwargs):
            code = self.perform('path:read_bytes', path)
            bindings = self.perform('path:read_bytes', bindings_path)
            if digest(code) != record['sha256'] or digest(bindings) != record['bindings_sha256']:
                raise Rejected('changed pinned module inputs')
            binding_value = getattr(module, 'binding')
            identity = relative + ':' + record['function'] + ':' + digest(code)
            return self.call(identity, [digest(bindings), binding_value], args, kwargs, function, import_ledger)

        setattr(module, record['function'], wrapped)

    def patch(self, target, name, replacement):
        self.original[(target, name)] = getattr(target, name)
        setattr(target, name, replacement)

    def __enter__(self):
        if self.active or Session.active_session is not None or not sys.dont_write_bytecode or threading.active_count() != 1:
            raise Rejected('requires one fresh isolated no-bytecode session')
        self.active = True
        Session.active_session = self
        path_names = ('read_bytes', 'stat', 'lstat', 'exists', 'is_file', 'is_dir', 'is_symlink', 'resolve', 'glob', 'rglob', 'iterdir')
        for name in path_names:
            original = getattr(Path, name)

            def invoke(path, *args, _name=name, _original=original, **kwargs):
                if self.internal or not self.frames:
                    return _original(path, *args, **kwargs)
                return self.perform('path:' + _name, path, args, kwargs)

            self.patch(Path, name, invoke)
        original_text = Path.read_text

        def read_text(path, encoding=None, errors=None, **kwargs):
            if self.internal or not self.frames:
                return original_text(path, encoding=encoding, errors=errors, **kwargs)
            data = self.perform('path:read_bytes', path)
            with io.TextIOWrapper(io.BytesIO(data), encoding=encoding, errors=errors, **kwargs) as stream:
                return stream.read()

        self.patch(Path, 'read_text', read_text)
        for name in ('stat', 'lstat', 'readlink', 'listdir'):
            original = getattr(os, name)

            def invoke(path, *args, _name=name, _original=original, **kwargs):
                if self.internal or not self.frames:
                    return _original(path, *args, **kwargs)
                return self.perform('os:' + _name, path, args, kwargs)

            self.patch(os, name, invoke)
        for target, name in ((builtins, 'open'), (io, 'open'), (io, 'open_code'), (os, 'open'),
                             (os, 'scandir'), (os, 'access'), (os, 'chdir'), (os, 'system'),
                             (subprocess, 'Popen'),
                             *((os, n) for n in ('unlink','remove','rename','replace','mkdir','rmdir',
                                'chmod','chown','truncate','link','symlink','utime','fork',
                                'posix_spawn','posix_spawnp','execv','execve','execvp','execvpe','read','write') if hasattr(os,n))):
            original = getattr(target, name)

            def denied(*args, _name=name, _original=original, **kwargs):
                if self.internal or not self.frames:
                    return _original(*args, **kwargs)
                raise Rejected('unrecorded or live operation: ' + _name)

            self.patch(target, name, denied)
        loader = importlib.machinery.SourceFileLoader

        def get_data(instance, path):
            if self.internal or not self.frames:
                return self.original[(loader, 'get_data')](instance, path)
            if not str(path).endswith('.py'):
                raise Rejected('bytecode/non-source loader input')
            return self.perform('path:read_bytes', path)

        def exec_module(instance, module):
            relative = os.path.relpath(os.path.abspath(instance.path), self.root)
            if not self.frames and relative not in self.functions:
                return self.original[(loader, 'exec_module')](instance, module)
            import_ledger = {}
            self.frames.append(import_ledger)
            try:
                path = self.path(instance.path)
                if not path.endswith('.py'):
                    raise Rejected('only exact Python source modules')
                body = self.perform('path:read_bytes', path)
                record = self.functions.get(os.path.relpath(path, self.root))
                if record and digest(body) != record['sha256']:
                    raise Rejected('changed allowlisted module before execution')
                code = compile(body, path, 'exec', dont_inherit=True)
                exec(code, module.__dict__)
                self.wrap_module(module, import_ledger)
            finally:
                self.frames.pop()

        self.patch(loader, 'get_data', get_data)
        self.patch(loader, 'exec_module', exec_module)
        return self

    def __exit__(self, *exception):
        for (target, name), original in reversed(list(self.original.items())):
            setattr(target, name, original)
        self.active = False
        Session.active_session = None
