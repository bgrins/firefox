fn parse(tokens: &mut std::str::SplitWhitespace<'_>) -> QueryCondition {
    let token = tokens.next().expect("node");
    let (kind, raw) = token.split_once(':').expect("tag");
    let id: u32 = raw.parse().expect("integer");
    match kind {
        "S" => QueryCondition::Style(StyleQuery(id)),
        "F" => QueryCondition::Feature(id),
        "C" => QueryCondition::Custom(id),
        "M" => QueryCondition::MozPref(id),
        "G" => QueryCondition::GeneralEnclosed(id.to_string(), 0, 0),
        "N" => QueryCondition::Not(Box::new(parse(tokens))),
        "P" => QueryCondition::InParens(Box::new(parse(tokens))),
        "A" | "O" => QueryCondition::Operation(
            (0..id).map(|_| parse(tokens)).collect::<Vec<_>>().into_boxed_slice(),
            if kind == "A" { Operator::And } else { Operator::Or },
        ),
        _ => panic!("unknown tag"),
    }
}

fn tag(node: &QueryCondition) -> String {
    match node {
        QueryCondition::Style(s) => format!("S:{}", s.0),
        QueryCondition::Feature(s) => format!("F:{}", s),
        QueryCondition::Custom(s) => format!("C:{}", s),
        QueryCondition::MozPref(s) => format!("M:{}", s),
        QueryCondition::GeneralEnclosed(s, _, _) => format!("G:{}", s),
        QueryCondition::Not(_) => "N:0".into(),
        QueryCondition::InParens(_) => "P:0".into(),
        QueryCondition::Operation(cs, op) => format!("{}:{}", if matches!(op, Operator::And) { "A" } else { "O" }, cs.len()),
    }
}

fn render(set: &AttrReferenceSet) -> String {
    set.iter().map(u32::to_string).collect::<Vec<_>>().join(",")
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    for line in input.lines() {
        let (seed, text) = line.split_once('|').unwrap();
        let mut tokens = text.split_whitespace();
        let node = parse(&mut tokens);
        assert!(tokens.next().is_none());
        let initial: AttrReferenceSet = seed.split(',').filter(|x| !x.is_empty()).map(|s| s.parse().unwrap()).collect();
        let mut result = initial.clone();
        node.collect_attribute_references(&mut result);
        let mut original = initial;
        node.original_collect_attribute_references(&mut original);
        let mut trace = Vec::new();
        node.visit(&mut |c| trace.push(tag(c)));
        println!("{}|{}|{}", render(&result), render(&original), trace.join(" "));
    }
}
