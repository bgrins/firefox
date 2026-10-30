#[derive(Clone, Copy)]
enum PublicationDemand {
    Ready,
    Metric(PrioritaryPropertyId),
    Unresolved,
}

#[derive(Clone)]
struct MetricAction {
    identity: Arc<()>,
    root: VarType,
    owner: VarType,
    index: usize,
    prerequisite: PrioritaryPropertyId,
}

enum MetricActionProgress {
    Published(PrioritaryPropertyId),
    AlreadyComplete,
    GeneratedPrerequisite(PrioritaryPropertyId),
    References(LonghandId, Arc<UnparsedValue>),
    Invalidated,
    Unsupported,
    WrongAction,
}
