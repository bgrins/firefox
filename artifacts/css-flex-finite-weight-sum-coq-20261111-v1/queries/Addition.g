@rnd = float<ieee_64,ne>;
raw = sum+weight;
next = rnd(raw);
{ sum in [0,1b192] /\ weight in [0,1b159] -> raw in [0,1b193] /\ next in [0,1b193] /\ next-sum in [-1b160,1b160] }
next-sum -> (next-raw)+weight;
