import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require isolated nonoptimized Python without site")
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
def body(text, anchor):
    if text.count(anchor) != 1:
        raise ValueError("nonunique source anchor: " + anchor)
    start = text.index(anchor)
    brace = text.index("{", start)
    depth, i, state = 0, brace, "code"
    while i < len(text):
        c, nxt = text[i], text[i:i+2]
        if state == "line":
            if c == "\n": state = "code"
        elif state == "block":
            if nxt == "*/": state = "code"; i += 1
        elif state in ("string", "char"):
            if c == "\\": i += 1
            elif c == ('"' if state == "string" else "'"): state = "code"
        elif nxt == "//": state = "line"; i += 1
        elif nxt == "/*": state = "block"; i += 1
        elif c == '"': state = "string"
        elif c == "'": state = "char"
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    raise ValueError("unterminated body")

def bindings():
    result=[]
    for file,entries in json.loads((ROOT/"BINDING-ANCHORS.json").read_text()).items():
        path=ROOT/"source"/file
        text=path.read_text()
        for name,anchor in entries:
            code=body(text,anchor)
            row={"name":name,"source":"source/"+file,"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"anchor":anchor,"body":code,"body_sha256":hashlib.sha256(code.encode()).hexdigest()}
            index=ROOT/"source"/file.replace('.local.','.indexed.')
            if index!=path and index.exists():
                row["indexed_body_equal"]=body(index.read_text(),anchor)==code
            result.append(row)
    return result
if __name__=="__main__": print(json.dumps(bindings(),indent=2))
