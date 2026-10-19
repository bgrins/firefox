int main() {
  int count, lineCount, clearanceId, outputPresent, initialEmpty, initialRetry;
  while (std::cin >> count >> lineCount >> clearanceId >> outputPresent >> initialEmpty >> initialRetry) {
    std::vector<std::unique_ptr<nsBlockFrame>> nodes;
    std::vector<std::tuple<int, int, int>> links;
    for (int i = 0; i < count; ++i) {
      auto node = std::make_unique<nsBlockFrame>();
      node->id = i;
      int parent, descend, next, clear;
      std::cin >> node->block >> node->selfEmpty >> node->empty >> node->hidden
               >> node->marginRoot >> node->intersect >> node->start >> node->end
               >> node->paddingStart >> node->paddingEnd >> node->preferred
               >> node->minimum >> clear >> parent >> descend >> next >> node->hasOverflow;
      node->display.mClear = clear ? StyleClear::Both : StyleClear::None;
      links.emplace_back(parent, descend, next);
      nodes.push_back(std::move(node));
    }
    auto ptr = [&](int id) -> nsIFrame* { return id < 0 ? nullptr : nodes.at(id).get(); };
    for (int i = 0; i < count; ++i) {
      nodes[i]->parent = ptr(std::get<0>(links[i]));
      nodes[i]->descend = ptr(std::get<1>(links[i]));
      nodes[i]->next = ptr(std::get<2>(links[i]));
    }
    for (int i = 0; i < lineCount; ++i) {
      int owner, overflow, child;
      Line line{};
      line.id = i;
      std::cin >> owner >> overflow >> line.inlined >> line.empty >> line.clearance >> child;
      line.mFirstChild = ptr(child);
      auto& target = overflow ? nodes.at(owner)->overflow.mLines : nodes.at(owner)->normal;
      target.push_back(line);
    }
    trace.clear(); constructed = destroyed = 0;
    bool empty = initialEmpty, retry = initialRetry;
    bool dirty;
    CollapsingMargin margin;
    {
      ReflowInput input(nodes.at(0).get());
      nsBlockReflowContext context;
      dirty = context.ComputeCollapsedBStartMargin(input, &margin, ptr(clearanceId), &retry, outputPresent ? &empty : nullptr);
    }
    CollapsingMargin pos = margin, neg = margin;
    pos.Include(-nscoord_MAX);
    neg.Include(nscoord_MAX);
    std::cout << margin.Get() << ' ' << static_cast<int64_t>(pos.Get()) + nscoord_MAX
              << ' ' << static_cast<int64_t>(neg.Get()) - nscoord_MAX << ' '
              << margin.IsZero() << ' ' << empty << ' ' << retry << ' ' << dirty
              << ' ' << constructed << ' ' << destroyed;
    std::vector<std::pair<int, int>> lineStates(lineCount);
    for (const auto& node : nodes) {
      for (const auto* lines : {&node->normal, &node->overflow.mLines}) {
        for (const auto& line : *lines) lineStates.at(line.id) = {line.clearance, line.dirty};
      }
    }
    for (auto [clearance, marks] : lineStates) std::cout << ' ' << clearance << ' ' << marks;
    std::cout << " |";
    for (auto [event, id] : trace) std::cout << ' ' << event << id;
    std::cout << '\n';
  }
}
