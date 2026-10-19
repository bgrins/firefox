struct AttrTaintedRange { start: usize, end: usize }
struct AttrTaint(Vec<AttrTaintedRange>);
impl AttrTaint {
    pub fn should_disallow_urls_in_range(&self, range: &AttrTaintedRange) -> bool {
        self.0
            .iter()
            .any(|r| r.start < range.end && r.end > range.start)
    }
}

fn main() {
    let mut cases = 0;
    let mut mismatches = 0;
    for a in 0..=5 {
        for b in a..=5 {
            for c in 0..=5 {
                for d in c..=5 {
                    let taint = AttrTaint(vec![AttrTaintedRange { start: a, end: b }]);
                    let url = AttrTaintedRange { start: c, end: d };
                    let expected = (0..5).any(|byte| (a..b).contains(&byte) && (c..d).contains(&byte));
                    mismatches += usize::from(taint.should_disallow_urls_in_range(&url) != expected);
                    cases += 1;
                }
            }
        }
    }
    println!("{} {}", cases, mismatches);
    let max = usize::MAX;
    let cases = [
        (max - 1, max, max - 1, max, true),
        (max, max, max - 1, max, false),
        (max - 2, max - 1, max - 1, max, false),
        (0, max, max, max, false),
        (0, 0, 0, max, false),
    ];
    let actual: Vec<bool> = cases.iter().map(|&(a,b,c,d,_)| {
        AttrTaint(vec![AttrTaintedRange { start: a, end: b }])
            .should_disallow_urls_in_range(&AttrTaintedRange { start: c, end: d })
    }).collect();
    println!("{:?}", actual);
}
