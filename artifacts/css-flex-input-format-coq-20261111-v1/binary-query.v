Require Import Reals ZArith Gappa.Gappa_library Flocq.IEEE754.Binary.
Check Binary.binary_float.
Check Binary.B2R.
Check Binary.is_finite.
Check Binary.generic_format_B2R.
Check Binary.B2R_lt_emax.
Check Binary.valid_binary.
Search (Rabs (Binary.B2R _ _ _) < _)%R.
Search (Generic_fmt.generic_format _ _ (Binary.B2R _ _ _)).
