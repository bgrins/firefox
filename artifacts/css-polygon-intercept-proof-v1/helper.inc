inline nscoord NSCoordMulDiv(nscoord aMult1, nscoord aMult2, nscoord aDiv) {
  return int64_t(aMult1) * int64_t(aMult2) / int64_t(aDiv);
}
