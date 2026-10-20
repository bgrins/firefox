import hashlib,json,pathlib,re,sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError("use -I -S")
r=pathlib.Path(__file__).resolve().parent
files=json.loads((r/"FILES.json").read_text())
assert {p.relative_to(r).as_posix() for p in r.rglob("*") if p.is_file()}==set(files)|{"FILES.json","FREEZE.json"}
for n,h in files.items():
 p=r/n
 assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==h,n
assert hashlib.sha256((r/"FILES.json").read_bytes()).hexdigest()==json.loads((r/"FREEZE.json").read_text())["files_sha256"]
for mode in ["canonical","relocated"]:
 result=json.loads((r/mode/"RESULT.json").read_text());assert result["status"]=="PASS" and result["audits"]==37 and result["bindings"]==10
 commands=json.loads((r/mode/"COMMANDS.json").read_text());assert len(commands)==10
 assert [c["exit"] for c in commands]==[0]*5+[42]*5
 for c,label in zip(commands[5:],["ascii escaped","metadata escaped","no-reset comment","normalized escaped","inner block"]):assert "SEMANTIC_MISMATCH "+label in c["stdout"]
 reports=re.findall(r"'(TerminalSpan\.\w+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",commands[3]["stdout"],re.S)
 assert len(reports)==37
negative=json.loads((r/"NEGATIVES.json").read_text());assert len(negative)==10
assert all(c["exit"]!=0 and c["output_absent"] for c in negative)
print("PASS retained canonical/relocated/37-audit/5-mutant/10-guard receipts")
