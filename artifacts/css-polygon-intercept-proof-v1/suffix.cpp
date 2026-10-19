int main(int argc, char** argv) {
  if (argc != 2) return 2;
  const std::string mode(argv[1]);
  nscoord x1, y1, x2, y2, y;
  while (std::cin >> x1 >> y1 >> x2 >> y2 >> y) {
    const nsPoint a{x1,y1}, b{x2,y2};
    const nscoord result = mode == "old"
        ? before::nsFloatManager::PolygonShapeInfo::XInterceptAtY(y,a,b)
        : nsFloatManager::PolygonShapeInfo::XInterceptAtY(y,a,b);
    std::cout << result << '\n';
  }
  return std::cin.eof() ? 0 : 2;
}
