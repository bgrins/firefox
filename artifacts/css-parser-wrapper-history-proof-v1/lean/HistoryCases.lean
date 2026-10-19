import PublicByteWitnesses
namespace HistoryCases
def cases : List (List PublicCache.Byte × List String) := [
 ([118,97,114,40,45,45,120,41],["enable:var", "save", "fetch", "reset:0", "fetch", "query"]),
 ([118,97,114,40,45,45,120,41],["save", "fetch", "reset:0", "enable:var", "fetch", "query"]),
 ([118,97,114,40,45,45,120,41],["enable:var", "save", "fetch", "query", "reset:0", "enable:var", "fetch", "query"]),
 ([99,97,108,99,40,118,97,114,40,45,45,120,41,41],["enable:var", "fetch", "fetch", "query"]),
 ([118,92,54,49,32,114,40,45,45,120,41],["enable:var", "fetch", "query"]),
 ([86,97,82,40,45,45,120,41],["enable:var", "fetch", "query"]),
 ([85,82,76,40,32,13,10,34,118,97,114,40,34,41],["enable:url", "fetch", "query"]),
 ([117,114,108,40,118,97,114,41],["enable:url", "fetch", "query"]),
 ([119,105,100,116,104,58,118,97,114,40,45,45,120,41],["fetch", "fetch", "enable:var", "save", "fetch", "reset:0", "fetch", "query"]),
 ([40,93,118,97,114,40,45,45,120,41,41,116,97,105,108],["enable:var", "fetch", "fetch", "query"]),
 ([40,47,42,35,32,115,111,117,114,99,101,85,82,76,61,65,32,42,47,41,47,42,35,32,115,111,117,114,99,101,85,82,76,61,66,32,42,47],["fetch", "save", "fetch", "reset:0", "fetch", "fetch"]),
 ([40,47,42,35,32,115,111,117,114,99,101,77,97,112,112,105,110,103,85,82,76,61,65,32,42,47,41,47,42,35,32,115,111,117,114,99,101,77,97,112,112,105,110,103,85,82,76,61,66,32,42,47],["fetch", "save", "fetch", "reset:0", "fetch", "fetch"]),
 ([118,97,114,40,45,45,120,41,59,101,110,118,40,41],["enable:var,env", "fetch", "stop", "query", "enable:env", "fetch", "fetch", "query"]),
 ([],["enable:var", "fetch", "fetch", "query", "query"])
]
end HistoryCases
