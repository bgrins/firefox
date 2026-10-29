# Incremental sibling-count build disk assessment

The completed one-source candidate build had92 volume-wide samples over91.66seconds: start30.0497GiB, minimum28.3642GiB, final29.5791GiB. Its maximum sampled draw is1.68551GiB, larger than the historical seven-build maximum1.438GiB. The actual inner result has exit0, no error/stop, no cleanup errors and absent owned group.

Root reports32.755GiB currently available and estimates29.56GiB after the required backup. Repeating the latest sampled draw would leave about27.87GiB, versus the existing15GiB monitored stop. For this same incremental one-Rust-file build with -j2, a reviewed experiment-local29GiB admission is proportionate. Owner before/after-backup and builder checks must agree. Retain15GiB running stop and every ownership/restoration check. This is not appropriate evidence for a clean/full build, and one-second volume samples neither isolate compiler allocations nor guarantee future peak usage or exclude unrelated writers.

No additional deletion or current objdir sweep was performed. Prior narrow cleanup removed the independently verified obsolete LF symbols; no further safely obsolete0.5GiB package has been established by this review. A fresh broad search is not justified merely to satisfy a conservative internal30GiB admission threshold. Root owns the policy decision. No helper, source, index, canonical epoch or runtime was changed.

Evidence reads4c785d/fac667; prior disk report8d482d. MEASUREMENT.json pins actual log/result and calculation inputs. No additional build/browser/process action was performed.
