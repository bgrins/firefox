# Random rollback control after line-height fix 141

This 26-test successor strengthens the successful unitless line-height control: the explicit-key reference must resolve to at least 10px for a 10px font and a random multiplier between 1 and 3, and target and reference computed values must agree. This prevents the previous zero/zero computed result from passing vacuously. The specified-key assertion remains. The other 25 callbacks and names are unchanged.

The test requires the accepted contextual line-height fix 141 (975e651729ba). It accompanies corrected four-source random rollback proposal v4 and adds no new bug count. Registered random tests remain unchanged. Destination: testing/web-platform/tests/css/css-values/random-typed-parse-rollback.html.

Node syntax and registration checks pass. One synthetic positive and two deliberately false computed-value controls exercise the strengthened assertions; these are not browser results. Paired browser validation remains pending. The sealed v3 proposal and existing live older WPT remain untouched.
