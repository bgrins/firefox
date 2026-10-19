# Parser nesting-limit recovery

The local Firefox WPT reproduces one declaration-recovery failure: an inner
color declaration becomes visible after depth rejection in inline padding-left.
Nine other padding cases and ten width controls pass. Both test harnesses finish
normally, with fixed source/configuration/binary pins before and after the run.

Root replay authenticates the static scout and reproduces all 16 actual parser
API/declaration observations. The reduced property callback is not full Gecko;
the browser run establishes this particular caller bridge. The complete parser
source retrieved through Searchfox matches the live source.

The bug was found by static inspection during formal verification work. Repair
and formal recovery model remain pending, as does independent adjudication.
No native source change or accepted native-fix count is attached to this record.
