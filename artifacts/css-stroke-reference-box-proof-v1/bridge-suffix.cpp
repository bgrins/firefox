}
using namespace nsStyleTransformMatrix;
void Emit(const TransformReferenceBox& box, const nsIFrame& frame) {
  std::cout << int(box.mIsCached) << ' ' << box.mBox.x << ' ' << box.mBox.y << ' '
            << box.mBox.width << ' ' << box.mBox.height;
  for (int count : frame.counts) { std::cout << ' ' << count; }
}
int main() {
  int tag, svg, cached, needs, divisor, absent;
  while (std::cin >> tag >> svg >> cached >> needs >> divisor >> absent) {
    nsIFrame frame{};
    frame.svg = svg;
    frame.display.mTransformBox = StyleTransformBox(tag);
    frame.style.zoom = {divisor, &frame.counts};
    for (nsRect* rect : {&frame.content, &frame.border, &frame.svgRect}) {
      std::cin >> rect->x >> rect->y >> rect->width >> rect->height;
    }
    nsRect initial;
    std::cin >> initial.x >> initial.y >> initial.width >> initial.height;
    TransformReferenceBox box{bool(cached), absent ? nullptr : &frame, bool(needs), initial};
    box.EnsureDimensionsAreCached();
    Emit(box, frame);
    std::cout << '|';
    box.EnsureDimensionsAreCached();
    Emit(box, frame);
    std::cout << '\n';
  }
}
