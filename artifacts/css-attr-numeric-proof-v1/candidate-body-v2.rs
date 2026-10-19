parser.skip_whitespace();
let start = parser.position();
parser.expect_number().ok()?;
let mut s = String::from(parser.slice_from(start));
parser.expect_exhausted().ok()?;
s.push_str(unit);
Some(s)
