enum NodePublication<T> {
    SemanticOpen,
    CycleUnsettled,
    Pending(T),
    Applying,
    Complete,
    CycleSettled,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum NodeReadiness {
    SemanticOpen,
    ComputationPending,
    Complete,
    CycleSettled,
}

impl<T> NodePublication<T> {
    fn readiness(&self) -> NodeReadiness {
        match self {
            Self::SemanticOpen => NodeReadiness::SemanticOpen,
            Self::CycleUnsettled | Self::Pending(_) | Self::Applying => {
                NodeReadiness::ComputationPending
            },
            Self::Complete => NodeReadiness::Complete,
            Self::CycleSettled => NodeReadiness::CycleSettled,
        }
    }

    fn close(&mut self, value: T) {
        assert!(matches!(self, Self::SemanticOpen));
        *self = Self::Pending(value);
    }

    fn take_ready(&mut self, prerequisites_ready: bool) -> Option<T> {
        if !prerequisites_ready {
            return None;
        }
        assert!(matches!(self, Self::Pending(_)));
        let Self::Pending(value) = std::mem::replace(self, Self::Applying) else {
            unreachable!()
        };
        Some(value)
    }

    fn finish(&mut self) {
        assert!(matches!(self, Self::Applying));
        *self = Self::Complete;
    }

    fn begin_cycle(&mut self) {
        assert!(matches!(self, Self::SemanticOpen));
        *self = Self::CycleUnsettled;
    }

    fn settle_cycle(&mut self) {
        assert!(matches!(self, Self::CycleUnsettled));
        *self = Self::CycleSettled;
    }

    fn can_retire(&self) -> bool {
        matches!(self, Self::Complete | Self::CycleSettled)
    }
}
