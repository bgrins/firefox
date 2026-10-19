int main() {
  nscoord extent, spacing, base;
  int32_t span;
  while (std::cin >> extent >> spacing >> span >> base) {
    nscoord result = base;
    const nscoord share = candidate(extent, spacing, span, result);
    std::cout << original(extent, spacing, span) << ' ' << share << ' '
              << allocation(extent, spacing, span) << ' ' << result << '\n';
  }
  return std::cin.eof() ? 0 : 2;
}
