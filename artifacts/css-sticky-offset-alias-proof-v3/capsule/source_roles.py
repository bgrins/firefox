import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import hashlib,json

RECEIPTS={
    "CANDIDATE.json":"78ae38936d3192db250e3e87b4797997e6539e59b9b134475c0352e0a2db3679",
    "BUILD-v1.json":"354377c5a25e26203c1ccb7e38487959a4887d792d5433083cc4d2323d98bc28",
    "FORMAT-TRANSFER.json":"d56de254963393d397fc3761f3f7f8d6a77bee4689efad223068c8151aa12453",
    "TESTED-RUN.json":"550fd2088e13449b86f40292d452957e9680670d40a6c9f8b274e8e8bff33e25",
    "BEFORE-RUN.json":"f25b53a6f03c38426aa9e2e48ed61e9e22f0b21607209b5a5cc31e1439ae72e6",
}

def require(condition,message):
    if not condition:raise RuntimeError("source role: "+message)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(root):
    receipts={}
    for name,digest in RECEIPTS.items():
        path=root/"receipts"/name
        require(sha(path)==digest,"canonical receipt identity "+name)
        receipts[name]=json.loads(path.read_text())
    candidate=receipts["CANDIDATE.json"]
    build=receipts["BUILD-v1.json"]
    transfer=receipts["FORMAT-TRANSFER.json"]
    roles={"before.cpp":candidate["before_sha256"],
           "candidate.cpp":candidate["candidate_sha256"],
           "candidate-formatted.cpp":transfer["after_sha256"]}
    require(len(set(roles.values()))==3,"three distinct sources")
    require(build["exit"]==0 and build["compiled_source_sha256"]==roles["candidate.cpp"],"compiled tested source")
    require(transfer["before_sha256"]==roles["candidate.cpp"] and transfer["compiled_source_was_preformat"] is True and transfer["other_source_bytes_unchanged"] is True,"preformat transfer")
    for name,role,phase,exitcode in [("BEFORE-RUN.json","before.cpp","baseline",1),("TESTED-RUN.json","candidate.cpp","candidate",0)]:
        run=receipts[name]
        require(run["phase"]==phase and run["complete"] is True and run["status"]=="done" and run["exit"]==exitcode,"completed browser record "+name)
        require(run["stable_pins"] is True and run["before"]==run["after"],"stable canonical live record "+name)
        require(run["before"][candidate["native_file"]]==roles[role],"canonical live source "+name)
    for name,digest in roles.items():
        require(sha(root/"inputs"/name)==digest,"exact input "+name)
    pins=json.loads((root/"SOURCE-PINS.json").read_text())["files"]
    require(set(pins)==set(roles)|{"nsCoord.h","LayoutConstants.h"},"source pin roster")
    require(all(pins[name]==digest for name,digest in roles.items()),"source pin role mapping")
    for name,digest in pins.items():require(sha(root/"inputs"/name)==digest,"source pin identity "+name)
    return {"files":roles,"receipt_hashes":RECEIPTS,"canonical_preformat_record":"receipts/TESTED-RUN.json","distinct_source_files":3}
