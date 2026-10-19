int main() {
  int fit, cw, ch, hasWidth, width, hasHeight, height, present, numerator, denominator;
  while (std::cin >> fit >> cw >> ch >> hasWidth >> width >> hasHeight >> height
                  >> present >> numerator >> denominator) {
    IntrinsicSize intrinsic;
    if (hasWidth) { intrinsic.width = width; }
    if (hasHeight) { intrinsic.height = height; }
    ratioCalls = 0;
    const nsSize result = ComputeConcreteObjectSize({cw,ch}, intrinsic,
        {bool(present),numerator,denominator}, StyleObjectFit(fit));
    std::cout << result.width << ' ' << result.height << ' ' << ratioCalls << '\n';
  }
}
