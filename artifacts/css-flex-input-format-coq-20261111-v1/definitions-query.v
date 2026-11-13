Require Import Reals ZArith Gappa.Gappa_library.
Check FLT.generic_inclusion_FLT_FLT.
Check Generic_fmt.generic_inclusion.
Search (Generic_fmt.generic_format _ _ (IZR _)).
Check FLT.FLT_format.
Check FLT.generic_format_FLT.
Check FLT.FLT_format_generic.
Search (Generic_fmt.generic_format _ _ _ -> Generic_fmt.generic_format _ _ _).
