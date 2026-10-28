# Compile correction for the normalization experiment

The first experimental build failed with E0599: PropertyId has no is_custom method. This version replaces that call in the two CSSOM length conversions with an explicit PropertyId::Custom match. The other five candidate bodies and all HEAD bases remain the exact v2 captures. The seven-file normalization experiment remains unaccepted, with the same container-contract and logical-unit scheduling limitations.
