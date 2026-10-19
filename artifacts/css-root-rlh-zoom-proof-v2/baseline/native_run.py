import json
import os
from pathlib import Path
import subprocess
import sys
import cases
import extract
import mutants
BASE=Path(__file__).resolve().parent

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    events=cases.generate();protocol=cases.protocol(events)
    (out/"events.json").write_text(json.dumps(events,indent=2)+"\n")
    (out/"input.txt").write_text(protocol)
    commands=[]
    for name,variant,mutation in [("original","original",0),("candidate","candidate",0)]+[(n,"candidate",i) for i,n in mutants.NAMES.items()]:
        folder=out/name;extract.generate(folder,variant)
        if mutation:
            f=folder/"style.inc";f.write_text(mutants.mutate(f.read_text(),mutation))
        cpp=folder/"provider.o"
        build_cpp=["clang++","-std=c++17","-O0","-I",str(folder),"-c",str(BASE/"native/provider.cpp"),"-o",str(cpp)]
        env=dict(os.environ,RLH_EXTRACTED=str((folder/"style.inc").resolve()),RLH_MUTANT=str(mutation))
        binary=folder/"native"
        build_rs=["rustc","--edition=2021",str(BASE/"native/style.rs"),"-C","link-arg="+str(cpp.resolve()),"-C","link-arg=-lc++","-o",str(binary)]
        for command in [build_cpp,build_rs]:
            result=subprocess.run(command,capture_output=True,text=True,env=env)
            commands.append(dict(command=command,variant=name,exit=result.returncode,stdout=result.stdout,stderr=result.stderr))
            assert result.returncode==0,result.stderr
        result=subprocess.run([str(binary)],input=protocol,capture_output=True,text=True)
        (folder/"raw.jsonl").write_text(result.stdout)
        (folder/"stderr.txt").write_text(result.stderr)
        assert result.returncode==0,(name,result.stderr)
        rows=[json.loads(x) for x in result.stdout.splitlines()]
        assert len(rows)==len(events)
    (out/"commands.json").write_text(json.dumps(commands,indent=2)+"\n")
    print(json.dumps({"events":len(events),"reads":sum(e['event']=='READ' for e in events),"variants":12}))
if __name__=="__main__":run(Path(sys.argv[1]).resolve())
