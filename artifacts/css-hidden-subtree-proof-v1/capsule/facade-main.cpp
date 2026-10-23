int main() {
  int id = 0;
  for (int produce = 0; produce < 2; ++produce)
  for (int hidden = 0; hidden < 2; ++hidden)
  for (unsigned mask = 0; mask < 128; ++mask)
  for (unsigned hm = 0; hm < 4; ++hm)
  for (int tm = 0; tm < 3; ++tm) {
    Document document;
    PresShell shell;
    shell.mDocument = &document;
    CandidateFlex root;
    nsIFrame f[10];
    root.shell = &shell;
    root.hidden = hidden;
    root.state = mask & 64 ? NS_FRAME_IS_DIRTY : 0;
    for (int i = 1; i <= 9; ++i) { f[i].id = i; f[i].shell = &shell; }
    for (int i = 1; i <= 6; ++i) f[i].state = mask & (1u << (i - 1)) ? NS_FRAME_IS_DIRTY : 0;
    if (hm & 1) f[1].AddStateBits(NS_FRAME_HAS_DIRTY_CHILDREN);
    if (hm & 2) f[4].AddStateBits(NS_FRAME_HAS_DIRTY_CHILDREN);
    f[1].table = tm == 2;
    f[2].table = tm == 1;
    root.lists = {{{&f[1], &f[6]}}, {{&f[7]}}};
    f[1].lists = {{{&f[2]}}, {{&f[3]}}};
    f[2].lists = {{{&f[4]}}};
    f[3].lists = {{{&f[5]}}};
    f[1].parent = f[6].parent = f[7].parent = &root;
    f[2].parent = f[3].parent = &f[1];
    f[4].parent = &f[2];
    f[5].parent = &f[3];
    if (produce) ProduceDirty(&f[1]);
    root.HiddenGuard();
    std::cout << id++ << ',' << root.HasAnyStateBits(NS_FRAME_IS_DIRTY);
    for (int n : {1, 2, 4, 3, 5, 6, 7, 8, 9}) {
      int before = shell.forces;
      shell.EnsureReflowIfFrameHasHiddenContent(&f[n]);
      std::cout << ',' << n << ',' << f[n].HasAnyStateBits(NS_FRAME_IS_DIRTY)
                << ',' << f[n].IsSubtreeDirty() << ',' << (shell.forces - before);
      assert(shell.mHiddenContentInForcedLayout.IsEmpty());
    }
    std::cout << '\n';
  }
}
