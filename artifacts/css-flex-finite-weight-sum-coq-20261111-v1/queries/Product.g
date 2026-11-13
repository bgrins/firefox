@rnd = float<ieee_64,ne>;
weight = rnd(factor*base);
{ factor in [0,1b128] /\ base in [0,1b31] -> factor*base in [0,1b159] /\ weight in [0,1b159] }
