Require Import ReverseTarget ReverseSign ReverseStructure ReverseBinding ReverseSafety ReverseJoint.

Theorem full_reverse_target : FullReverseTarget.
Proof.
  exact (conj sign_target (conj remainder_target (conj reverse_count_target
    (conj reverse_order_target (conj event_binding_target (conj trace_target
    (conj reverse_safety_target (conj conservation_target
    (conj reverse_branches_target reverse_joint_target))))))))).
Qed.

Print Assumptions full_reverse_target.
