
fn main() {
    let inputs = ["0.5".to_owned(), "5e-1".to_owned(), format!("5{}e-309", "0".repeat(308)), format!("5{}e-400", "0".repeat(399)), format!("0.{}5e399", "0".repeat(399)), "0e999".to_owned(), "1e999".to_owned(), format!("17{}e-308px", "0".repeat(308)), "17px".to_owned()];
    for (i,input) in inputs.iter().enumerate() {
        let mut p = Parser { input, position: 0 };
        let token = consume_numeric(&mut p);
        assert_eq!(p.position, input.len());
        println!("case={i}\tconsumed={}\ttoken={token:?}", p.position);
    }
}
