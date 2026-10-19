fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    for line in input.lines() {
        let fields: Vec<i32> = line.split_whitespace().map(|s| s.parse().unwrap()).collect();
        assert_eq!(fields.len(), 4);
        let ty = ContainerType(fields[0] as u8);
        let wm = WritingMode(fields[1] != 0);
        let size = ContainerSizeQueryResult {
            width: if fields[2] >= 0 { Some(fields[2]) } else { None },
            height: if fields[3] >= 0 { Some(fields[3]) } else { None },
        };
        let (width, height) = match mask(ty, wm, size) {
            TraversalResult::Done(result) => (result.width.unwrap_or(-1), result.height.unwrap_or(-1)),
            TraversalResult::InProgress => (-1, -1),
        };
        println!("{} {} {}", container_type_axes(ty, wm).0, width, height);
    }
}
