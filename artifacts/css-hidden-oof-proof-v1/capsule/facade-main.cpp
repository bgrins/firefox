int main() {
  int row = 0;
  for (int timing = 0; timing < 3; ++timing)
    for (int dm = 0; dm < 8; ++dm)
      for (int hm = 0; hm < 4; ++hm)
        for (int ph = 0; ph < 2; ++ph)
          for (int next = 0; next < 2; ++next)
            for (int differs = 0; differs < 2; ++differs)
              for (int table = 0; table < 2; ++table)
                for (int owner = 0; owner < 2; ++owner)
                  for (int anon = 0; anon < 2; ++anon) {
                    PresShell shell;
                    nsIFrame root, mid, leaf, flow, host, physicalOwner, placeholder;
                    for (nsIFrame* f : {&root, &mid, &leaf, &flow, &host, &physicalOwner, &placeholder}) {
                      f->shell = &shell;
                      f->first = f;
                    }
                    root.parent = &physicalOwner;
                    root.placeholder = &placeholder;
                    placeholder.parent = &flow;
                    flow.parent = &host;
                    flow.hidden = ph;
                    flow.state = NS_FRAME_OWNS_ANON_BOXES;
                    physicalOwner.hidden = owner;
                    root.state = (dm & 1) | ((hm & 1) << 1) | NS_FRAME_OUT_OF_FLOW;
                    mid.state = (dm >> 1) & 1;
                    leaf.state = ((dm >> 2) & 1) | (hm & 2);
                    mid.table = table;
                    root.next = next;
                    root.style.anon = anon;
                    root.lists[0].mList = {&mid};
                    mid.parent = &root;
                    mid.lists[0].mList = {&leaf};
                    leaf.parent = &mid;
                    inputDiffers = differs;
                    bool resize = Execute(timing, &root);
                    bool rootEligible = root.IsSubtreeDirty(), leafEligible = leaf.IsSubtreeDirty();
                    shell.UpdateHiddenContentInForcedLayout(&leaf);
                    auto r = root.rect;
                    std::cout << row++ << ',' << timing << ',' << dm << ',' << hm << ','
                              << ph << ',' << next << ',' << differs << ',' << table << ','
                              << owner << ',' << anon << ',' << resize << ','
                              << (root.state & 3) << ',' << (mid.state & 3) << ',' << (leaf.state & 3) << ','
                              << rootEligible << ',' << leafEligible << ',' << shell.forces << ','
                              << r.x << ',' << r.y << ',' << r.w << ',' << r.h << '\n';
                  }
}
