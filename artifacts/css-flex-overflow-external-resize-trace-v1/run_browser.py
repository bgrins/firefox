import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib, json, subprocess, threading, time, shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
OUT=ROOT/sys.argv[1]
OUT.mkdir()
REPO=ROOT.parent.parent
BINARY=REPO/"objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox"
if sys.argv[1].startswith("release"): BINARY=Path("/Applications/Firefox.app/Contents/MacOS/firefox")
PATHS=[BINARY,BINARY.parent/"XUL",REPO/"layout/generic/nsFlexContainerFrame.cpp",REPO/"layout/generic/nsContainerFrame.cpp",REPO/"layout/generic/nsColumnSetFrame.cpp",ROOT/"probe.html",Path(__file__).resolve()]
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        while chunk:=f.read(1024*1024): h.update(chunk)
    return h.hexdigest()
before={str(p):digest(p) for p in PATHS}
rows=[]
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path!="/":self.send_error(404);return
        body=(ROOT/"probe.html").read_bytes()
        self.send_response(200);self.send_header("Content-Type","text/html");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def do_POST(self):
        rows.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(204);self.end_headers()
server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
profile=OUT/"profile";profile.mkdir()
command=[str(BINARY),"-headless","-no-remote","-profile",str(profile),f"http://127.0.0.1:{server.server_port}/"]
with (OUT/"browser.log").open("w") as log:
    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    try:
        deadline=time.monotonic()+30
        while time.monotonic()<deadline and process.poll() is None and not rows:time.sleep(.1)
    finally:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait()
server.shutdown();thread.join();shutil.rmtree(profile)
after={str(p):digest(p) for p in PATHS}
result={"command":command,"before":before,"after":after,"stable":before==after,"observations":rows,"exit_after_termination":process.returncode,"profile_removed":True,"run_kind":sys.argv[1]}
(OUT/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"stable":result["stable"],"posts":len(rows),"rows":sum(len(o.get("rows",[])) for o in rows),"errors":[o for o in rows if "error" in o]},indent=2))
assert len(rows)==1 and len(rows[0].get("rows",[]))==8
if not rows or before!=after:raise RuntimeError("Incomplete or unstable run")
