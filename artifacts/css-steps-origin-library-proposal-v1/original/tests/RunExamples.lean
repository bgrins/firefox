import CssSemantics

open CssSemantics

def main : IO Unit := do
  for test in ExecutableExamples.cases do
    let actual := test.selector.matchesBool Examples.forest test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for test in LogicalExamples.cases do
    let actual := test.expression.matchesBool Examples.forest test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for test in SiblingExamples.cases do
    let actual := test.expression.matchesBool SiblingExamples.forest test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for test in AttributeExamples.cases do
    let actual := test.selector.matchesBool test.attributes
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for (name, formula, index, expected) in AnBExamples.cases do
    let actual := formula.matchesBool index
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: {actual}"
  for test in StructuralExamples.cases do
    let actual := test.selector.matchesBool SiblingExamples.forest test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for (name, actual, expected) in StructuralExamples.namespaceChecks do
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: {actual}"
  for test in RelativeExamples.cases do
    let actual := HasSelector.matchesBool RelativeExamples.forest test.selectors test.anchor
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for (name, actual, expected) in RelativeExamples.negationCases do
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: {actual}"
  for test in SyntaxExamples.cases do
    let actual := SyntaxList.matchingSpecificity SyntaxExamples.forest test.selectors test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {repr test.expected}, got {repr actual}")
    IO.println s!"PASS {test.name}: {actual.isSome}"
  for test in CombinedExamples.cases do
    let actual := test.selector.matchesBool RelativeExamples.forest test.node
    let weight := test.selector.specificity
    unless actual == test.expectedMatch && weight == test.expectedSpecificity do
      throw (IO.userError s!"FAIL {test.name}: got {actual}, {repr weight}")
    IO.println s!"PASS {test.name}: {actual}"
  for test in DefaultingExamples.cases do
    let actual := resolve ⟨test.inherited, 0⟩ test.parent test.cascaded
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: true"
  for (name, node, expected) in DefaultingExamples.chainCases do
    let actual := computeProperty Examples.forest DefaultingExamples.inheritedProfile
      DefaultingExamples.declarations node
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: true"
  for (name, node, expected) in DefaultingExamples.noninheritedCases do
    let actual := computeProperty Examples.forest DefaultingExamples.noninheritedProfile
      DefaultingExamples.noninheritedDeclarations node
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: true"
  for (name, entries, expected) in CascadeExamples.cases do
    let actual := (Cascade.winner entries).map CascadeEntry.value
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {repr expected}, got {repr actual}")
    IO.println s!"PASS {name}: {actual.isSome}"
  for test in StyleExamples.cases do
    let actual := Style.cascaded StyleExamples.forest test.rules test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {repr test.expected}, got {repr actual}")
    IO.println s!"PASS {test.name}: {actual.isSome}"
  for (name, node, expected) in StyleExamples.chainCases do
    let actual := Style.compute StyleExamples.chainForest StyleExamples.chainProfile StyleExamples.chainRules node
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: true"
  for test in BrowserFixtures.cases do
    let actual := test.selector.matchesBool BrowserFixtures.forest test.node
    unless actual == test.expectedBool do
      throw (IO.userError s!"FAIL browser {test.name}: expected {test.expectedBool}, got {actual}")
    IO.println s!"PASS browser {test.name}: {actual}"
  for test in ContentExamples.cases do
    let profile := if test.draftWhitespace then ContentExamples.whitespaceProfile else EmptyProfile.strictText
    let actual := test.selector.matchesBool ContentExamples.context profile test.node
    unless actual == test.expected && test.selector.specificity == test.specificity do
      throw (IO.userError s!"FAIL {test.name}: got {actual}, {repr test.selector.specificity}")
    IO.println s!"PASS {test.name}: {actual}"
  for (name, items, draft, expected) in ContentExamples.textCases do
    let actual := ContentList.emptyBool (if draft then ContentExamples.whitespaceProfile else .strictText) items
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: {actual}"
  for test in ContextStyleExamples.cases do
    let actual := GenericStyle.cascaded (ContextStyleExamples.model test.draft) test.rules test.node
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {repr test.expected}, got {repr actual}")
    IO.println s!"PASS {test.name}: {actual.isSome}"
  for (name, draft, node, expected) in ContextStyleExamples.computedCases do
    let actual := GenericStyle.compute (ContextStyleExamples.model draft)
      ContextStyleExamples.inheritedProfile ContextStyleExamples.inheritedRules node
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: true"
  let absent := ContextSyntax.root.matchesBool ContextStyleExamples.noDocumentContext .strictText .root
  unless absent == false do
    throw (IO.userError "FAIL context absent document root")
  IO.println s!"PASS context absent document root: {absent}"
  for test in RecursiveExamples.cases do
    let actual := (RecursiveExamples.model test.draft).matchesBool test.selector test.node
    unless actual == test.expected && test.selector.specificity == test.weight && test.selector.noNestedHas do
      throw (IO.userError s!"FAIL {test.name}: got {actual}, {repr test.selector.specificity}")
    IO.println s!"PASS {test.name}: {actual}"
  for (name, selector, expected) in RecursiveExamples.restrictionCases do
    let actual := selector.noNestedHas
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: {actual}"
  for (name, rules, node, expected) in RecursiveExamples.styleCases do
    let actual := GenericStyle.cascaded (RecursiveExamples.model false) rules node
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {repr expected}, got {repr actual}")
    IO.println s!"PASS {name}: {actual.isSome}"
  for test in ContentBrowserFixtures.cases do
    let actual := test.selector.matchesBool ContentBrowserFixtures.context .strictText test.node
    unless actual == test.expectedBool && test.selector.noNestedHas do
      throw (IO.userError s!"FAIL {test.name}: got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for test in ContentBrowserFixtures.observations do
    let actual := test.selector.matchesBool ContentBrowserFixtures.context ContentExamples.whitespaceProfile test.node
    unless actual == test.expectedBool && test.selector.noNestedHas do
      throw (IO.userError s!"FAIL {test.name}: got {actual}")
    IO.println s!"PASS {test.name}: {actual}"
  for scenario in ComputedBrowserFixtures.scenarios do
    for query in scenario.queries do
      let actual := Style.compute ComputedBrowserFixtures.forest ComputedBrowserFixtures.propertyProfile scenario.rules query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for test in VariablesExamples.cases do
    let actual := test.expression.substitute VariablesExamples.environment
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {repr test.expected}, got {repr actual}")
    IO.println s!"PASS {test.name}: true"
  for (name, actual, expected) in VariablesExamples.graphCases do
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {expected}, got {actual}")
    IO.println s!"PASS {name}: {actual}"
  for test in VariablesSolverExamples.cases do
    let actual := test.bindings.compute test.property
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {repr test.expected}, got {repr actual}")
    IO.println s!"PASS {test.name}: true"
  for (name, node, property, expected) in VariablesInheritanceExamples.cases do
    let actual := VariableEnvironment.compute VariablesInheritanceExamples.forest
      VariablesInheritanceExamples.declarations node property
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {repr expected}, got {repr actual}")
    IO.println s!"PASS {name}: true"
  for test in VariablePropertyExamples.cases do
    let actual := VariableProperty.compute KeywordToken.decode VariablePropertyExamples.environment
      ⟨test.inherited, 7⟩ test.parent test.winner
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {test.expected}, got {actual}")
    IO.println s!"PASS {test.name}: true"
  for (name, tokens, expected) in VariablePropertyExamples.decoderCases do
    let actual := KeywordToken.decode tokens
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {repr expected}, got {repr actual}")
    IO.println s!"PASS {name}: true"
  for scenario in VariablesBrowserFixtures.scenarios do
    for query in scenario.queries do
      let actual := VariableStyle.compute VariablesBrowserFixtures.model scenario.declarations
        scenario.rules KeywordToken.decode ComputedBrowserFixtures.propertyProfile query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for test in GuardedExamples.cases do
    let actual := GuardedSolver.compute test.bindings test.base test.property
    unless actual == test.expected do
      throw (IO.userError s!"FAIL {test.name}: expected {repr test.expected}, got {repr actual}")
    IO.println s!"PASS {test.name}: true"
  for (name, active, marks, property, expected) in GuardedExamples.stateCases do
    let actual := (GuardedSolver.resolve (fun _ => (none : Option (List Nat))) [] active marks property).2
    unless actual == expected do
      throw (IO.userError s!"FAIL {name}: expected {repr expected}, got {repr actual}")
    IO.println s!"PASS {name}: true"
  for scenario in GuardedBrowserFixtures.scenarios do
    for query in scenario.queries do
      let actual := GenericVariableStyle.compute .guarded VariablesBrowserFixtures.model
        scenario.declarations scenario.rules KeywordToken.decode ComputedBrowserFixtures.propertyProfile query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for test in KeywordExamples.cases do
    for (label, variables) in [("snapshot", ExecutableVariableModel.snapshotKeywords),
        ("guarded", ExecutableVariableModel.guardedKeywords)] do
      let actual := variables.compute test.bindings test.base test.property
      let name := label ++ " " ++ test.name
      unless actual == test.expected do
        throw (IO.userError s!"FAIL {name}: expected {repr test.expected}, got {repr actual}")
      IO.println s!"PASS {name}: true"
  for scenario in KeywordBrowserFixtures.scenarios do
    for query in scenario.queries do
      let actual := GenericVariableStyle.compute .guardedKeywords VariablesBrowserFixtures.model
        scenario.declarations scenario.rules KeywordToken.decode ComputedBrowserFixtures.propertyProfile query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for scenario in CustomStyleExamples.scenarios do
    for query in scenario.queries do
      let actual := CustomStyle.compute .guardedKeywords VariablesBrowserFixtures.model
        scenario.customRules scenario.ordinaryRules KeywordToken.decode ComputedBrowserFixtures.propertyProfile query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for scenario in LayerExamples.scenarios do
    for query in scenario.queries do
      let actual := LayerStyle.compute VariablesBrowserFixtures.model scenario.rules
        ComputedBrowserFixtures.propertyProfile query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for scenario in LayerCustomExamples.scenarios do
    for query in scenario.queries do
      let actual := LayerCustomStyle.compute .guardedKeywords VariablesBrowserFixtures.model
        scenario.customRules scenario.ordinaryRules KeywordToken.decode ComputedBrowserFixtures.propertyProfile query.node
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless actual == query.expected do
        throw (IO.userError s!"FAIL {name}: expected {query.expected.cssValue}, got {actual.cssValue}")
      IO.println s!"PASS {name}: true"
  for test in RawValueExamples.cases do
    unless ValueSyntax.parseRaw test.source == test.expected do
      throw (IO.userError s!"FAIL raw {test.name}")
    IO.println s!"PASS raw {test.name}: true"
  for (name, passed) in RawValueExamples.stateChecks do
    unless passed do throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for scenario in ParsedBrowserFixtures.scenarios do
    for query in scenario.queries do
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless ParsedBrowserFixtures.compute scenario query.node == some query.expected do
        throw (IO.userError s!"FAIL {name}")
      IO.println s!"PASS {name}: true"
  for test in ScopeExamples.matchCases do
    unless ScopedElement.elementMatches ScopeExamples.context .strictText test.selector test.node == test.expected do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"
  for test in ScopeExamples.closestCases do
    unless ScopedElement.closest ScopeExamples.context .strictText test.selector test.node == test.expected do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"
  for test in ScopeExamples.queryCases do
    unless ScopedElement.queryMemberBool ScopeExamples.context .strictText test.selector test.receiver test.candidate == test.expected do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"
  for (name, passed) in ScopeExamples.contextCases do
    unless passed do throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for test in OrderedQueryExamples.cases do
    let actual := OrderedQueries.all OrderedQueryExamples.context .strictText test.selector test.receiver
    let first := OrderedQueries.first OrderedQueryExamples.context .strictText test.selector test.receiver
    unless actual == test.expected && first == test.expected.head? do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name} all: true"
    IO.println s!"PASS {test.name} first: true"

  for test in ParsedSelectorExamples.cases do
    unless SelectorText.parseRaw test.source == test.expected do
      throw (IO.userError s!"FAIL selector raw {test.name}")
    IO.println s!"PASS selector raw {test.name}: true"
  for (name, source, expected) in ParsedSelectorExamples.specificityCases do
    unless (SelectorText.parseRaw source).map (List.map SelectorText.Chain.specificity) == some expected do
      throw (IO.userError s!"FAIL selector {name}")
    IO.println s!"PASS selector {name}: true"
  for (name, source, expected) in ParsedSelectorExamples.matchingCases do
    let actual := (SelectorText.parseQuery source).map fun selector =>
      ScopedElement.elementMatches OrderedQueryExamples.context .strictText selector .p
    unless actual == some expected do
      throw (IO.userError s!"FAIL selector {name}")
    IO.println s!"PASS selector {name}: true"
  for test in ParsedSelectorBrowserFixtures.cases do
    unless ParsedSelectorBrowserFixtures.all test == some test.expected &&
        ParsedSelectorBrowserFixtures.first test == some test.expected.head? do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name} all: true"
    IO.println s!"PASS {test.name} first: true"

  for test in ParsedSelectorsExamples.cases do
    unless ParsedSelectors.parse test.source == test.expected do
      throw (IO.userError s!"FAIL style selector {test.name}")
    IO.println s!"PASS style selector {test.name}: true"
  for (name, source, expected) in ParsedSelectorsExamples.weightCases do
    unless ParsedSelectorsExamples.weightResult source == expected do
      throw (IO.userError s!"FAIL style selector {name}")
    IO.println s!"PASS style selector {name}: true"
  for scenario in ParsedStyleExamples.scenarios do
    for query in scenario.queries do
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless ParsedStyleExamples.compute scenario query.node == some query.expected do
        throw (IO.userError s!"FAIL {name}")
      IO.println s!"PASS {name}: true"

  for test in AttributeParserExamples.cases do
    unless SelectorText.parseRaw test.source == test.expected do
      throw (IO.userError s!"FAIL parser {test.name}")
    IO.println s!"PASS parser {test.name}: true"
  for (name, source, expected) in AttributeParserExamples.facadeCases do
    unless (ParsedSelectors.parse source).isSome == expected do
      throw (IO.userError s!"FAIL parser {name}")
    IO.println s!"PASS parser {name}: true"
  for (name, source, expected) in AttributeParserExamples.specificityCases do
    unless (SelectorText.parseRaw source).map (List.map SelectorText.Chain.specificity) == some expected do
      throw (IO.userError s!"FAIL parser {name}")
    IO.println s!"PASS parser {name}: true"
  for test in AttributeBrowserFixtures.cases do
    unless AttributeBrowserFixtures.all test == some test.expected &&
        AttributeBrowserFixtures.first test == some test.expected.head? do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name} all: true"
    IO.println s!"PASS {test.name} first: true"

  for test in StructuralPseudoExamples.cases do
    unless test.check do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"
  for test in StructuralBrowserFixtures.cases do
    unless StructuralBrowserFixtures.evaluate .strictText test == some test.expected do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"
  for test in StructuralBrowserFixtures.observations do
    unless StructuralBrowserFixtures.evaluate ContentExamples.whitespaceProfile test == some test.expected do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"

  for (name, accepted) in AnBTextExamples.tokenChecks ++ AnBTextExamples.roundtripChecks ++
      AnBSourceExamples.checks ++ AnBSourceExamples.unsupportedChecks ++ AnBBrowserFixtures.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"

  for test in AnBTokensExamples.cases do
    unless test.check do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"

  for (name, accepted) in FunctionBodyExamples.checks ++ FunctionTokenExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for test in IndexedPseudoExamples.cases do
    unless test.check do
      throw (IO.userError s!"FAIL {test.name}")
    IO.println s!"PASS {test.name}: true"
  for (name, accepted) in IndexedBrowserFixtures.checks ++ IndexedBrowserFixtures.unsupportedChecks ++
      IndexedBrowserFixtures.specificityChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"

  for (name, accepted) in ScopedScopeFreeExamples.checks ++ OfArgumentExamples.checks ++
      OfBrowserFixtures.checks ++ OfBrowserFixtures.unsupportedChecks ++ OfBrowserFixtures.specificityChecks ++
      OfBrowserFixtures.facadeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in NegationFunctionExamples.checks ++ NegationFunctionExamples.rejectionChecks ++
      NegationBrowserFixtures.checks ++ NegationBrowserFixtures.unsupportedChecks ++
      NegationBrowserFixtures.specificityChecks ++ NegationBrowserFixtures.facadeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in RecursiveSelectorBrowserFixtures.checks ++ RecursiveSelectorBrowserFixtures.unsupportedChecks ++
      RecursiveSelectorBrowserFixtures.specificityChecks ++ RecursiveSelectorBrowserFixtures.facadeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in EmptySelectorSourceExamples.checks ++ LogicalSelectorBrowserFixtures.checks ++
      LogicalSelectorBrowserFixtures.unsupportedChecks ++ LogicalSelectorBrowserFixtures.specificityChecks ++
      LogicalSelectorBrowserFixtures.facadeChecks ++ LogicalSelectorBrowserFixtures.observationChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in RelativeChainExamples.checks ++ RelativeChainExamples.propertyChecks ++
      HasSelectorBrowserFixtures.checks ++ HasSelectorBrowserFixtures.unsupportedChecks ++
      HasSelectorBrowserFixtures.specificityChecks ++ HasSelectorBrowserFixtures.facadeChecks ++
      HasSelectorBrowserFixtures.observationChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssInputExamples.checks ++ CssEscapeExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssNameClassesExamples.checks ++ CssNameExamples.checks ++
      CssNameExamples.consumptionChecks ++ CssNameExamples.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssHashExamples.checks ++ CssHashExamples.fallbackChecks ++
      CssHashExamples.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssUrlDispatchExamples.checks ++ CssIdentLikeExamples.checks ++
      CssIdentLikeExamples.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssUrlRecoveryExamples.checks ++ CssUrlTokenExamples.bodyChecks ++
      CssUrlTokenExamples.fullChecks ++ CssUrlTokenExamples.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssStringTokenExamples.checks ++ CssStringTokenExamples.rawChecks ++
      CssStringTokenExamples.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssCommentsExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssNumberExamples.checks ++ CssNumericTokenExamples.checks ++
      CssNumberValueExamples.checks ++ CssNumberCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssUnicodeRangeExamples.checks ++ CssUnicodeRangeExamples.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssAtKeywordExamples.checks ++ CssTokenizerExamples.checks ++
      CssTokenizationExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssComponentTypesExamples.checks ++ CssComponentTypesExamples.equalityChecks ++
      CssComponentExamples.sourceChecks ++ CssComponentExamples.listChecks ++ CssComponentExamples.oneChecks ++
      CssComponentCanonicalExamples.checks ++ CssComponentCanonicalExamples.boundaryChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssCommaExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSingleComponentExamples.checks ++ CssSingleComponentExamples.tokenChecks ++
      CssSingleCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ComponentSelectorTokensExamples.checks ++ ComponentSelectorTokensExamples.listChecks ++
      ComponentSelectorBrowserFixtures.checks ++ ComponentSelectorBrowserFixtures.unsupportedChecks ++
      ComponentSelectorBrowserFixtures.specificityChecks ++ ComponentSelectorDiagnostics.checks ++
      ComponentSelectorCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ComponentAttributeExamples.tokenChecks ++ ComponentAttributeExamples.listChecks ++
      ComponentAttributeExamples.diagnosticChecks ++ ComponentAttributeBrowserFixtures.checks ++
      ComponentAttributeBrowserFixtures.unsupportedChecks ++ ComponentAttributeBrowserFixtures.discrepancyChecks ++
      ComponentAttributeBrowserFixtures.specificityChecks ++ ComponentAttributeCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssIntegerTokenBridgeExamples.checks ++ CssIntegerTokenBridgeExamples.sourceChecks ++
      ComponentAnBExamples.checks ++ ComponentAnBExamples.diagnosticChecks ++
      ComponentAnBBrowserFixtures.checks ++ ComponentAnBCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ComponentFunctionTokensExamples.checks ++ ComponentIndexedBrowserFixtures.checks ++
      ComponentIndexedBrowserFixtures.unsupportedChecks ++ ComponentIndexedBrowserFixtures.specificityChecks ++
      ComponentIndexedDiagnostics.checks ++ ComponentIndexedCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ComponentOfArgumentExamples.checks ++ ComponentOfArgumentExamples.splitChecks ++
      RecursiveComponentBrowserFixtures.checks ++ RecursiveComponentBrowserFixtures.unsupportedChecks ++
      RecursiveComponentBrowserFixtures.specificityChecks ++ RecursiveComponentDiagnostics.checks ++
      RecursiveComponentCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in EmptyComponentListExamples.checks ++ LogicalComponentBrowserFixtures.checks ++
      LogicalComponentBrowserFixtures.unsupportedChecks ++ LogicalComponentBrowserFixtures.specificityChecks ++
      LogicalComponentBrowserFixtures.observationChecks ++ LogicalComponentDiagnostics.checks ++
      LogicalComponentCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ComponentRelativeExamples.listChecks ++ ComponentRelativeExamples.prefixChecks ++
      HasComponentBrowserFixtures.checks ++ HasComponentBrowserFixtures.unsupportedChecks ++
      HasComponentBrowserFixtures.specificityChecks ++ HasComponentBrowserFixtures.observationChecks ++
      HasComponentDiagnostics.checks ++ HasComponentCanonicalExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for scenario in ComponentStyleExamples.scenarios do
    unless scenario.queries.all (fun query => decide (ComponentStyleExamples.compute scenario query.node = some query.expected)) do
      throw (IO.userError s!"FAIL {scenario.name}")
    IO.println s!"PASS {scenario.name}: true"
  for (name, accepted) in ComponentStyleBoundaries.checks ++ ComponentStyleAdmissionExamples.checks ++
      ComponentStyleBoundaries.controls do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ForgivingComponentFixtures.checks ++ ForgivingComponentFixtures.wrapperChecks ++
      ForgivingComponentFixtures.unsupportedChecks ++ ForgivingComponentFixtures.weightChecks ++
      ForgivingComponentDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ForgivingHasFixtures.checks ++ ForgivingHasFixtures.unsupportedChecks ++
      ForgivingHasFixtures.weightChecks ++ ForgivingHasDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for scenario in ForgivingHasStyleExamples.scenarios do
    unless scenario.queries.all (fun query => decide (ForgivingHasStyleExamples.compute scenario query.node = some query.expected)) do
      throw (IO.userError s!"FAIL {scenario.name}")
    IO.println s!"PASS {scenario.name}: true"
  for (name, accepted) in ForgivingHasStyleExamples.boundaryChecks ++ ForgivingHasStyleExamples.scopeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssAnyValueExamples.sourceChecks ++ CssAnyValueExamples.domainChecks ++
      NumericBranchExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CertifiedComponentFixtures.checks ++ CertifiedComponentFixtures.wrapperChecks ++
      CertifiedComponentFixtures.unsupportedChecks ++ CertifiedComponentFixtures.weightChecks ++
      CertifiedComponentDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CertifiedRecoveryFixtures.checks ++ CertifiedRecoveryFixtures.unsupportedChecks ++
      CertifiedRecoveryFixtures.weightChecks ++ CertifiedRecoveryDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for scenario in CertifiedRecoveryStyleExamples.scenarios do
    unless scenario.queries.all (fun query => decide (CertifiedRecoveryStyleExamples.compute scenario query.node = some query.expected)) do
      throw (IO.userError s!"FAIL {scenario.name}")
    IO.println s!"PASS {scenario.name}: true"
  for (name, accepted) in CertifiedRecoveryStyleExamples.boundaryChecks ++ CertifiedRecoveryStyleExamples.scopeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ForbiddenSelectorBranchExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ForbiddenRecoveryFixtures.checks ++ ForbiddenRecoveryFixtures.unsupportedChecks ++
      ForbiddenRecoveryFixtures.weightChecks ++ ForbiddenRecoveryDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for scenario in ForbiddenRecoveryStyleExamples.scenarios do
    unless scenario.queries.all (fun query => decide (ForbiddenRecoveryStyleExamples.compute scenario query.node = some query.expected)) do
      throw (IO.userError s!"FAIL {scenario.name}")
    IO.println s!"PASS {scenario.name}: true"
  for (name, accepted) in ForbiddenRecoveryStyleExamples.boundaryChecks ++ ForbiddenRecoveryStyleExamples.scopeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in ExplicitTypeHeadExamples.checks ++ ExplicitTypeHeadExamples.weightChecks ++
      ExplicitTypeHeadFixtures.checks ++ ExplicitTypeHeadFixtures.unsupportedChecks ++
      ExplicitTypeHeadDiagnostics.checks ++ ExplicitTypeHeadDiagnostics.canonicalChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssDeclarationPriorityExamples.checks ++ CssDeclarationExamples.checks ++
      CssDeclarationContextExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssDeclarationEntryExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssInputTraceExamples.checks ++ CssInputTraceExamples.boundaryChecks ++
      CssSourceTraceExamples.checks ++ CssSourceTraceExamples.rangeChecks ++ CssSourceTraceExamples.rawChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssComponentClosureExamples.checks ++ CssComponentTraceExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssAtRulePrefixExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssDeclarationListExamples.checks ++ CssDeclarationListExamples.resolutionChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssRuleStructureExamples.checks ++ CssRuleExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssStylesheetExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssNumericTypeExamples.checks ++ CssNumericTypeAdditionExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssCalculationTypingExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssCalcUnitExamples.checks ++ CssCalcSourceExamples.syntaxChecks ++ CssCalcSourceExamples.typeChecks ++ CssCalcDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssScopeRegionExamples.checks ++ CssScopedCascadeExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for scenario in CssScopeFixtures.scenarios do
    for query in scenario.queries do
      let name := scenario.name ++ "/" ++ ComputedBrowserFixtures.nodeName query.node
      unless CssScopeFixtures.compute scenario query.node == query.expected do
        throw (IO.userError s!"FAIL {name}")
      IO.println s!"PASS {name}: true"
  for (name, accepted) in CssFiniteCalculationExamples.checks ++ CssFiniteScalarExamples.checks ++ CssUnitCalculationExamples.checks ++ CssUnitFactorExamples.checks ++ CssUnitScalarExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssCalcMagnitudeExamples.checks ++ CssCalcMagnitudeTerminalExamples.checks ++ CssCalcValueDiagnostics.checks ++ CssCalcValueExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssExtendedScalarExamples.checks ++ CssExceptionalKeywordExamples.checks ++ CssExceptionalExamples.checks ++ CssExceptionalDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssIntegerRoundingExamples.checks ++ CssFinalizedExamples.checks ++ CssFinalizedDiagnostics.checks ++ CssOpacityFixtures.checks ++ CssOpacityFixtures.boundaries ++ CssOpacityFixtures.controls do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssRelativeUnitExamples.checks ++ CssEnvironmentExamples.checks ++ CssEnvironmentDiagnostics.checks ++ CssEnvironmentFinalizationExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssNumericCollectionExamples.checks ++ CssNumericCollectionExamples.extractionChecks ++ CssResidualExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssComparisonScalarExamples.checks ++ CssComparisonExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssNumericCategoryExamples.checks ++ CssMathSyntaxExamples.checks ++ CssMathSyntaxExamples.unsupportedChecks ++ CssMathSourceExamples.checks ++ CssMathDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssProductPhaseExamples.checks ++ CssProductReadinessExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssTypeTransportExamples.checks ++ CssSumTypeExamples.checks ++ CssTypedResidualExamples.structuralChecks ++ CssTypedResidualExamples.eligibilityChecks ++ CssTypedResidualExamples.loweringChecks ++ CssTypedProductSourceExamples.checks ++ CssTypedProductDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssTypedResolutionExamples.resolutionChecks ++ CssTypedResolutionExamples.transportChecks ++ CssTypedNormalizationExamples.normalizationChecks ++ CssTypedNormalizationExamples.boundaryChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssCalculationPlanExamples.checks ++ CssCalculationPlanExamples.unsupportedChecks ++ CssCalculationConstructionExamples.checks ++ CssCalculationConstructionTraceExamples.assemblyChecks ++ CssCalculationConstructionTraceExamples.boundaryChecks ++ CssCalculationConstructionDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssComparisonReadinessExamples.checks ++ CssResidualComparisonExamples.checks ++ CssResidualComparisonCompositionExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssRecursiveResidualEmbeddingExamples.checks ++ CssRecursiveComparisonTreeExamples.checks ++ CssRecursiveResidualNormalizationExamples.normalizationChecks ++ CssRecursiveResidualNormalizationExamples.boundaryChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssComparisonPlanExamples.checks ++ CssComparisonPlanExamples.unsupportedChecks ++ CssComparisonConstructionTraceExamples.checks ++ CssComparisonConstructionTraceExamples.boundaryChecks ++ CssComparisonConstructionExamples.checks ++ CssComparisonConstructionExamples.boundaryChecks ++ CssComparisonConstructionDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssEnvironmentExtensionExamples.checks ++ CssStagedCalculationExamples.checks ++ CssStagedCalculationTraceExamples.checks ++ CssStagedCalculationNumericExamples.checks ++ CssStagedCalculationDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssStagedFinalizationExamples.checks ++ CssStagedOpacityExamples.checks ++ CssStagedFinalizationDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssVisibilityDeclarationExamples.checks ++ CssVisibilityStylesheetExamples.checks ++ CssVisibilityStylesheetDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostAttributeExamples.checks ++ HostCompoundFixtures.checks ++ HostCompoundFixtures.unsupportedChecks ++ HostCompoundDiagnostics.checks ++ HostCompoundDiagnostics.shapeChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostIdentityExamples.checks ++ HostIdentityCompoundSyntaxExamples.checks ++ HostIdentityCompoundSyntaxExamples.unsupportedChecks ++ HostIdentityCompoundFixtures.checks ++ HostIdentityCompoundFixtures.rawSnapshotChecks ++ HostIdentityCompoundDiagnostics.contextChecks ++ HostIdentityCompoundDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostSelectorContextExamples.checks ++ HostSelectorChainSyntaxExamples.checks ++ HostSelectorChainSyntaxExamples.unsupportedChecks ++ HostSelectorChainFixtures.checks ++ HostSelectorChainDiagnostics.checks ++ HostSelectorChainDiagnostics.weightChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostLogicalEmbeddingExamples.checks ++ HostLogicalSyntaxExamples.shapeChecks ++ HostLogicalSyntaxExamples.unsupportedChecks ++ HostLogicalSyntaxExamples.weightChecks ++ HostLogicalFixtures.checks ++ HostLogicalDiagnostics.checks ++ HostLogicalDiagnostics.contextChecks ++ HostLogicalDiagnostics.oldSourceChecks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostLogicalStyleExamples.checks ++ CssHostVisibilityFixtures.checks ++ CssHostVisibilityExamples.checks ++ CssHostVisibilityStylesheetDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostStructuralPrerequisiteExamples.checks ++ HostStructuralSyntaxExamples.shapeChecks ++ HostStructuralSyntaxExamples.unsupportedChecks ++ HostStructuralSyntaxExamples.weightChecks ++ HostStructuralFixtures.checks ++ HostStructuralDiagnostics.checks ++ HostStructuralDiagnostics.contextChecks ++ HostStructuralDiagnostics.oldSourceChecks ++ CssStructuralVisibilityFixtures.checks ++ CssStructuralVisibilityExamples.checks ++ CssStructuralVisibilityStylesheetDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in HostForgivingRecoveryExamples.checks ++ HostForgivingSyntaxExamples.shapeChecks ++ HostForgivingSyntaxExamples.unsupportedChecks ++ HostForgivingSyntaxExamples.weightChecks ++ HostForgivingFixtures.checks ++ HostForgivingDiagnostics.checks ++ HostForgivingDiagnostics.contextChecks ++ HostForgivingDiagnostics.oldSourceChecks ++ HostForgivingRecoveryViewExamples.checks ++ CssForgivingVisibilityFixtures.checks ++ CssForgivingVisibilityExamples.checks ++ CssForgivingVisibilityStylesheetDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.HostRelativeExamples.checks ++ HostRelationalSyntaxExamples.shapeChecks ++ HostRelationalSyntaxExamples.unsupportedChecks ++ HostRelationalSyntaxExamples.weightChecks ++ HostRelationalFixtures.checks ++ HostRelationalDiagnostics.checks ++ HostRelationalDiagnostics.contextChecks ++ HostRelationalDiagnostics.oldSourceChecks ++ CssRelationalVisibilityFixtures.checks ++ CssRelationalVisibilityExamples.checks ++ CssRelationalVisibilityStylesheetDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssLayerRegistryExamples.checks ++ CssLayerVisibilityFixtures.checks ++ CssLayerVisibilityDiagnostics.checks ++ CssLayerVisibilityExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssLayerHierarchyExamples.checks ++ CssNestedLayerVisibilityFixtures.checks ++ CssNestedLayerVisibilityDiagnostics.checks ++ CssNestedLayerVisibilityExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssLayerIdentityExamples.checks ++ CssAnonymousLayerVisibilityFixtures.checks ++ CssAnonymousLayerVisibilityDiagnostics.checks ++ CssAnonymousLayerVisibilityExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssGlobalConditionExamples.mediaChecks ++ CssGlobalConditionExamples.supportsChecks ++ CssConditionalLayerVisibilityFixtures.checks ++ CssConditionalLayerVisibilityDiagnostics.checks ++ CssConditionalLayerVisibilityExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssImportPrerequisiteExamples.headerChecks ++ CssSemantics.CssImportPrerequisiteExamples.identityChecks ++ CssSemantics.CssImportOccurrenceExamples.occurrenceChecks ++ CssSemantics.CssImportRuntimeExamples.runtimeChecks ++ CssSemantics.CssImportLayerVisibilityFixtures.checks ++ CssSemantics.CssImportLayerDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssRollbackPrerequisiteExamples.declarationChecks ++ CssSemantics.CssRollbackPrerequisiteExamples.traceChecks ++ CssSemantics.CssRollbackLayerVisibilityFixtures.checks ++ CssSemantics.CssRollbackLayerDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssAuthorSheetsIdentityExamples.checks ++ CssSemantics.CssAuthorSheetsFixtures.checks ++ CssSemantics.CssAuthorSheetsDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.AttachedLayerRollbackExamples.cases ++ CssSemantics.CssAttachedVisibilityFixtures.checks ++ CssSemantics.CssAttachedVisibilityDiagnostics.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssContainerPrerequisiteExamples.checks ++ CssSemantics.CssContainerGuardExamples.checks ++ CssSemantics.CssContainerSourceExamples.checks ++ CssSemantics.CssContainerSourceExamples.inheritedChecks ++ CssSemantics.CssContainerDiagnostics.checks ++ CssSemantics.CssContainerFixtures.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.OriginRollbackExamples.checks ++ CssSemantics.CssOriginDiagnostics.checks ++ CssSemantics.CssOriginFixtures.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssScopeResolutionExamples.checks ++ CssSemantics.CssScopeSelectorBoundaryExamples.checks ++ CssSemantics.CssSourceScopeExamples.checks ++ CssSemantics.CssSourceScopeFixtures.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssImplicitScopeExamples.checks ++ CssSemantics.CssOwnerScopeExamples.checks ++ CssSemantics.CssOwnerScopeFixtures.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CssScopeImportCoreExamples.checks ++ CssSemantics.CssScopeImportHostExamples.checks ++ CssSemantics.CssScopeImportFixtures.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.BaselineAlignmentExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.HitObservationExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.SvgLengthConversionExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.CounterGroupingExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.RelativeColorChannelsExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.ImplementationSupport.CounterProvenanceExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.ImplementationSupport.IntegerRoundingDyadicExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.ImplementationSupport.RoundRemainderExamples.checks do
    unless accepted do
      throw (IO.userError s!"FAIL {name}")
    IO.println s!"PASS {name}: true"
  for (name, accepted) in CssSemantics.SubgridExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.CounterRangeRepresentationExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.AdditiveOrderingExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.RoundRemainderCapacityExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.Binary32MagnitudeExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.CssFiniteRoundExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.RoundSpecialKnowledgeExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.FiniteModRemWitnessExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.FiniteModRemContractExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.KeyframeContextExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.KeyframeGraphExamples.checks do
    IO.println s!"PASS {name}: {accepted}"
  for (name, accepted) in CssSemantics.ImplementationSupport.KeyframeEndpointDefaultingExamples.checks do
    IO.println s!"PASS {name}: {accepted}"

  for (name, accepted) in CssSemantics.ImplementationSupport.CommitRefresh.checks do
    IO.println s!"PASS {name}: {accepted}"

  for (name, accepted) in CssSemantics.ImplementationSupport.KeyframeEndpointIndices.checks do
    IO.println s!"PASS {name}: {accepted}"

  for (name, accepted) in CssSemantics.GuardedNames.Examples.checks do
    IO.println s!"PASS {name}: {accepted}"
