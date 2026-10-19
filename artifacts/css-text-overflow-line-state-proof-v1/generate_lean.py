from pathlib import Path


def boolean(v):
    return 'true' if v else 'false'


def integer(v):
    return f'({v})' if v < 0 else str(v)


def style(s):
    if isinstance(s,dict):s=[s['kind'],s['width'],s['length']]
    return '{kind := %s, width := %s, length := %s}' % tuple(integer(int(v)) for v in s)


def optional(value,fn):
    return 'none' if value is None else '(some '+fn(value)+')'


def frame(f):
    return '{parent := %s, role := %s, visible := %s, nonsuppressed := %s, start := %s, size := %s, overflowStart := %s, overflowEnd := %s, advances := [%s]}' % (
        integer(f['parent']),f['role'],boolean(f['visible']),boolean(f['nonsuppressed']),integer(f['start']),integer(f['size']),
        *map(integer,f['overflow']),','.join(map(integer,f['advances'])))


def line(l):
    return '{frames := #[%s], overflowStart := %s, overflowEnd := %s, floats := %s, clamp := %s}' % (
        ','.join(map(frame,l['frames'])),*map(integer,l['overflow']),
        optional(l['floats'],lambda xs:'('+','.join(map(integer,xs))+')'),optional(l['clamp'],style))


def config(c):
    return '{id := %s, start := %s, width := %s, styles := #[%s], seed := %s, ellipsisWidth := %s, ellipsisFailure := %s, scroll := %s, snap := %s, units := %s, lines := [%s]}' % (
        c['id'],integer(c['start']),integer(c['width']),','.join(map(style,c['styles'])),boolean(c['seed']),integer(c['ellipsisWidth']),
        boolean(c['ellipsisFailure']),optional(c['scroll'],lambda xs:'('+','.join(map(integer,xs))+')'),boolean(c['snap']),integer(c['units']),','.join(map(line,c['lines'])))


def generate(rows):
    definitions='\n'.join(f'def fixture{c["id"]} : Config := {config(c)}' for c in rows)
    return '''import LineModel
open LineModel
set_option maxRecDepth 100000
set_option maxHeartbeats 0
'''+definitions+'\ndef fixtures : List Config := ['+','.join(f'fixture{c["id"]}' for c in rows)+''']
def showEvent (event : List Int) : String := "[" ++ String.intercalate "," (event.map toString) ++ "]"
def showTrace (events : Trace) : String := "[" ++ String.intercalate "," (events.map showEvent) ++ "]"
def main : IO Unit := do
  for candidate in [false,true] do
    for c in fixtures do
      match run c candidate with
      | .error e => throw (IO.userError (toString c.id ++ ": " ++ e))
      | .ok rows =>
        for (number,mode,events) in rows do
          IO.println ((if candidate then "candidate" else "original") ++ "\\t" ++ toString c.id ++ "\\t" ++ toString number ++ "\\t" ++ mode ++ "\\t" ++ showTrace events)
'''
