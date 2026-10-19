pub enum LonghandId {
        /// align-items
        AlignItems = 0,
        /// alignment-baseline
        AlignmentBaseline = 1,
        /// backface-visibility
        BackfaceVisibility = 2,
        /// baseline-source
        BaselineSource = 3,
        /// border-collapse
        BorderCollapse = 4,
        /// border-image-repeat
        BorderImageRepeat = 5,
        /// box-decoration-break
        BoxDecorationBreak = 6,
        /// box-sizing
        BoxSizing = 7,
        /// break-inside
        BreakInside = 8,
        /// caption-side
        CaptionSide = 9,
        /// clear
        Clear = 10,
        /// column-fill
        ColumnFill = 11,
        /// column-span
        ColumnSpan = 12,
        /// contain
        Contain = 13,
        /// container-type
        ContainerType = 14,
        /// content-visibility
        ContentVisibility = 15,
        /// direction
        Direction = 16,
        /// display
        Display = 17,
        /// dominant-baseline
        DominantBaseline = 18,
        /// empty-cells
        EmptyCells = 19,
        /// field-sizing
        FieldSizing = 20,
        /// flex-direction
        FlexDirection = 21,
        /// flex-wrap
        FlexWrap = 22,
        /// float
        Float = 23,
        /// font-kerning
        FontKerning = 24,
        /// font-language-override
        FontLanguageOverride = 25,
        /// font-optical-sizing
        FontOpticalSizing = 26,
        /// font-synthesis-style
        FontSynthesisStyle = 27,
        /// font-variant-caps
        FontVariantCaps = 28,
        /// font-variant-east-asian
        FontVariantEastAsian = 29,
        /// font-variant-emoji
        FontVariantEmoji = 30,
        /// font-variant-ligatures
        FontVariantLigatures = 31,
        /// font-variant-numeric
        FontVariantNumeric = 32,
        /// font-variant-position
        FontVariantPosition = 33,
        /// forced-color-adjust
        ForcedColorAdjust = 34,
        /// grid-auto-flow
        GridAutoFlow = 35,
        /// hyphens
        Hyphens = 36,
        /// image-orientation
        ImageOrientation = 37,
        /// image-rendering
        ImageRendering = 38,
        /// ime-mode
        ImeMode = 39,
        /// isolation
        Isolation = 40,
        /// justify-items
        JustifyItems = 41,
        /// line-break
        LineBreak = 42,
        /// list-style-position
        ListStylePosition = 43,
        /// margin-trim
        MarginTrim = 44,
        /// mask-type
        MaskType = 45,
        /// math-shift
        MathShift = 46,
        /// math-style
        MathStyle = 47,
        /// mix-blend-mode
        MixBlendMode = 48,
        /// -moz-box-align
        MozBoxAlign = 49,
        /// -moz-box-collapse
        MozBoxCollapse = 50,
        /// -moz-box-direction
        MozBoxDirection = 51,
        /// -moz-box-orient
        MozBoxOrient = 52,
        /// -moz-box-pack
        MozBoxPack = 53,
        /// -moz-control-character-visibility
        MozControlCharacterVisibility = 54,
        /// -moz-float-edge
        MozFloatEdge = 55,
        /// -moz-image-decoding
        MozImageDecoding = 56,
        /// -moz-inert
        MozInert = 57,
        /// -moz-math-variant
        MozMathVariant = 58,
        /// -moz-orient
        MozOrient = 59,
        /// -moz-osx-font-smoothing
        MozOsxFontSmoothing = 60,
        /// -moz-text-size-adjust
        MozTextSizeAdjust = 61,
        /// -moz-theme
        MozTheme = 62,
        /// -moz-top-layer
        MozTopLayer = 63,
        /// -moz-user-focus
        MozUserFocus = 64,
        /// -moz-window-dragging
        MozWindowDragging = 65,
        /// -moz-window-shadow
        MozWindowShadow = 66,
        /// object-fit
        ObjectFit = 67,
        /// outline-style
        OutlineStyle = 68,
        /// overflow-anchor
        OverflowAnchor = 69,
        /// overflow-wrap
        OverflowWrap = 70,
        /// page-orientation
        PageOrientation = 71,
        /// paint-order
        PaintOrder = 72,
        /// pointer-events
        PointerEvents = 73,
        /// position
        Position = 74,
        /// position-area
        PositionArea = 75,
        /// position-try-order
        PositionTryOrder = 76,
        /// position-visibility
        PositionVisibility = 77,
        /// print-color-adjust
        PrintColorAdjust = 78,
        /// resize
        Resize = 79,
        /// ruby-align
        RubyAlign = 80,
        /// ruby-position
        RubyPosition = 81,
        /// scroll-behavior
        ScrollBehavior = 82,
        /// scroll-snap-align
        ScrollSnapAlign = 83,
        /// scroll-snap-stop
        ScrollSnapStop = 84,
        /// scroll-snap-type
        ScrollSnapType = 85,
        /// scrollbar-gutter
        ScrollbarGutter = 86,
        /// scrollbar-width
        ScrollbarWidth = 87,
        /// shape-rendering
        ShapeRendering = 88,
        /// stroke-linecap
        StrokeLinecap = 89,
        /// stroke-linejoin
        StrokeLinejoin = 90,
        /// table-layout
        TableLayout = 91,
        /// text-align
        TextAlign = 92,
        /// text-align-last
        TextAlignLast = 93,
        /// text-anchor
        TextAnchor = 94,
        /// text-autospace
        TextAutospace = 95,
        /// text-box-edge
        TextBoxEdge = 96,
        /// text-box-trim
        TextBoxTrim = 97,
        /// text-combine-upright
        TextCombineUpright = 98,
        /// text-decoration-line
        TextDecorationLine = 99,
        /// text-decoration-skip-ink
        TextDecorationSkipInk = 100,
        /// text-decoration-style
        TextDecorationStyle = 101,
        /// text-emphasis-position
        TextEmphasisPosition = 102,
        /// text-justify
        TextJustify = 103,
        /// text-orientation
        TextOrientation = 104,
        /// text-rendering
        TextRendering = 105,
        /// text-transform
        TextTransform = 106,
        /// text-underline-position
        TextUnderlinePosition = 107,
        /// text-wrap-mode
        TextWrapMode = 108,
        /// text-wrap-style
        TextWrapStyle = 109,
        /// touch-action
        TouchAction = 110,
        /// transform-box
        TransformBox = 111,
        /// transform-style
        TransformStyle = 112,
        /// unicode-bidi
        UnicodeBidi = 113,
        /// user-select
        UserSelect = 114,
        /// vector-effect
        VectorEffect = 115,
        /// visibility
        Visibility = 116,
        /// -webkit-text-security
        WebkitTextSecurity = 117,
        /// white-space-collapse
        WhiteSpaceCollapse = 118,
        /// word-break
        WordBreak = 119,
        /// writing-mode
        WritingMode = 120,
        /// -x-text-scale
        XTextScale = 121,
        /// appearance
        Appearance = 122,
        /// -moz-default-appearance
        MozDefaultAppearance = 123,
        /// -moz-force-broken-image-icon
        MozForceBrokenImageIcon = 124,
        /// -moz-subtree-hidden-only-visually
        MozSubtreeHiddenOnlyVisually = 125,
        /// break-after
        BreakAfter = 126,
        /// break-before
        BreakBefore = 127,
        /// color-interpolation
        ColorInterpolation = 128,
        /// color-interpolation-filters
        ColorInterpolationFilters = 129,
        /// align-content
        AlignContent = 130,
        /// justify-content
        JustifyContent = 131,
        /// clip-rule
        ClipRule = 132,
        /// fill-rule
        FillRule = 133,
        /// align-self
        AlignSelf = 134,
        /// justify-self
        JustifySelf = 135,
        /// font-synthesis-position
        FontSynthesisPosition = 136,
        /// font-synthesis-small-caps
        FontSynthesisSmallCaps = 137,
        /// font-synthesis-weight
        FontSynthesisWeight = 138,
        /// overflow-block
        OverflowBlock = 139,
        /// overflow-inline
        OverflowInline = 140,
        /// overflow-x
        OverflowX = 141,
        /// overflow-y
        OverflowY = 142,
        /// overscroll-behavior-block
        OverscrollBehaviorBlock = 143,
        /// overscroll-behavior-inline
        OverscrollBehaviorInline = 144,
        /// overscroll-behavior-x
        OverscrollBehaviorX = 145,
        /// overscroll-behavior-y
        OverscrollBehaviorY = 146,
        /// border-block-end-style
        BorderBlockEndStyle = 147,
        /// border-block-start-style
        BorderBlockStartStyle = 148,
        /// border-bottom-style
        BorderBottomStyle = 149,
        /// border-inline-end-style
        BorderInlineEndStyle = 150,
        /// border-inline-start-style
        BorderInlineStartStyle = 151,
        /// border-left-style
        BorderLeftStyle = 152,
        /// border-right-style
        BorderRightStyle = 153,
        /// border-top-style
        BorderTopStyle = 154,
        /// column-rule-style
        ColumnRuleStyle = 155,
        /// accent-color
        AccentColor = 156,
        /// anchor-name
        AnchorName = 157,
        /// animation-composition
        AnimationComposition = 158,
        /// animation-delay
        AnimationDelay = 159,
        /// animation-direction
        AnimationDirection = 160,
        /// animation-duration
        AnimationDuration = 161,
        /// animation-fill-mode
        AnimationFillMode = 162,
        /// animation-iteration-count
        AnimationIterationCount = 163,
        /// animation-name
        AnimationName = 164,
        /// animation-play-state
        AnimationPlayState = 165,
        /// animation-range-end
        AnimationRangeEnd = 166,
        /// animation-range-start
        AnimationRangeStart = 167,
        /// animation-timeline
        AnimationTimeline = 168,
        /// animation-timing-function
        AnimationTimingFunction = 169,
        /// aspect-ratio
        AspectRatio = 170,
        /// backdrop-filter
        BackdropFilter = 171,
        /// background-attachment
        BackgroundAttachment = 172,
        /// background-blend-mode
        BackgroundBlendMode = 173,
        /// background-clip
        BackgroundClip = 174,
        /// background-image
        BackgroundImage = 175,
        /// background-origin
        BackgroundOrigin = 176,
        /// background-position-x
        BackgroundPositionX = 177,
        /// background-position-y
        BackgroundPositionY = 178,
        /// background-repeat
        BackgroundRepeat = 179,
        /// background-size
        BackgroundSize = 180,
        /// baseline-shift
        BaselineShift = 181,
        /// border-image-outset
        BorderImageOutset = 182,
        /// border-image-slice
        BorderImageSlice = 183,
        /// border-image-width
        BorderImageWidth = 184,
        /// border-spacing
        BorderSpacing = 185,
        /// box-shadow
        BoxShadow = 186,
        /// caret-color
        CaretColor = 187,
        /// clip
        Clip = 188,
        /// clip-path
        ClipPath = 189,
        /// color
        Color = 190,
        /// color-scheme
        ColorScheme = 191,
        /// column-count
        ColumnCount = 192,
        /// container-name
        ContainerName = 193,
        /// content
        Content = 194,
        /// counter-increment
        CounterIncrement = 195,
        /// counter-reset
        CounterReset = 196,
        /// counter-set
        CounterSet = 197,
        /// cursor
        Cursor = 198,
        /// d
        D = 199,
        /// filter
        Filter = 200,
        /// flex-basis
        FlexBasis = 201,
        /// font-family
        FontFamily = 202,
        /// font-feature-settings
        FontFeatureSettings = 203,
        /// font-palette
        FontPalette = 204,
        /// font-size
        FontSize = 205,
        /// font-size-adjust
        FontSizeAdjust = 206,
        /// font-style
        FontStyle = 207,
        /// font-variant-alternates
        FontVariantAlternates = 208,
        /// font-variation-settings
        FontVariationSettings = 209,
        /// font-weight
        FontWeight = 210,
        /// font-width
        FontWidth = 211,
        /// grid-template-areas
        GridTemplateAreas = 212,
        /// hyphenate-character
        HyphenateCharacter = 213,
        /// hyphenate-limit-chars
        HyphenateLimitChars = 214,
        /// initial-letter
        InitialLetter = 215,
        /// letter-spacing
        LetterSpacing = 216,
        /// line-clamp
        LineClamp = 217,
        /// line-height
        LineHeight = 218,
        /// link-parameters
        LinkParameters = 219,
        /// list-style-type
        ListStyleType = 220,
        /// mask-clip
        MaskClip = 221,
        /// mask-composite
        MaskComposite = 222,
        /// mask-image
        MaskImage = 223,
        /// mask-mode
        MaskMode = 224,
        /// mask-origin
        MaskOrigin = 225,
        /// mask-position-x
        MaskPositionX = 226,
        /// mask-position-y
        MaskPositionY = 227,
        /// mask-repeat
        MaskRepeat = 228,
        /// mask-size
        MaskSize = 229,
        /// math-depth
        MathDepth = 230,
        /// -moz-context-properties
        MozContextProperties = 231,
        /// -moz-min-font-size-ratio
        MozMinFontSizeRatio = 232,
        /// offset-anchor
        OffsetAnchor = 233,
        /// offset-path
        OffsetPath = 234,
        /// offset-position
        OffsetPosition = 235,
        /// offset-rotate
        OffsetRotate = 236,
        /// outline-offset
        OutlineOffset = 237,
        /// overflow-clip-margin
        OverflowClipMargin = 238,
        /// page
        Page = 239,
        /// perspective
        Perspective = 240,
        /// position-anchor
        PositionAnchor = 241,
        /// position-try-fallbacks
        PositionTryFallbacks = 242,
        /// quotes
        Quotes = 243,
        /// rotate
        Rotate = 244,
        /// scale
        Scale = 245,
        /// scroll-timeline-axis
        ScrollTimelineAxis = 246,
        /// scroll-timeline-name
        ScrollTimelineName = 247,
        /// scrollbar-color
        ScrollbarColor = 248,
        /// shape-outside
        ShapeOutside = 249,
        /// size
        Size = 250,
        /// stroke-dasharray
        StrokeDasharray = 251,
        /// stroke-dashoffset
        StrokeDashoffset = 252,
        /// stroke-width
        StrokeWidth = 253,
        /// tab-size
        TabSize = 254,
        /// text-decoration-inset
        TextDecorationInset = 255,
        /// text-decoration-thickness
        TextDecorationThickness = 256,
        /// text-emphasis-style
        TextEmphasisStyle = 257,
        /// text-indent
        TextIndent = 258,
        /// text-overflow
        TextOverflow = 259,
        /// text-shadow
        TextShadow = 260,
        /// text-underline-offset
        TextUnderlineOffset = 261,
        /// transform-origin
        TransformOrigin = 262,
        /// transition-behavior
        TransitionBehavior = 263,
        /// transition-delay
        TransitionDelay = 264,
        /// transition-duration
        TransitionDuration = 265,
        /// transition-property
        TransitionProperty = 266,
        /// transition-timing-function
        TransitionTimingFunction = 267,
        /// translate
        Translate = 268,
        /// view-timeline-axis
        ViewTimelineAxis = 269,
        /// view-timeline-inset
        ViewTimelineInset = 270,
        /// view-timeline-name
        ViewTimelineName = 271,
        /// view-transition-class
        ViewTransitionClass = 272,
        /// view-transition-name
        ViewTransitionName = 273,
        /// -webkit-text-stroke-width
        WebkitTextStrokeWidth = 274,
        /// will-change
        WillChange = 275,
        /// word-spacing
        WordSpacing = 276,
        /// -x-lang
        XLang = 277,
        /// z-index
        ZIndex = 278,
        /// zoom
        Zoom = 279,
        /// object-position
        ObjectPosition = 280,
        /// perspective-origin
        PerspectiveOrigin = 281,
        /// fill
        Fill = 282,
        /// stroke
        Stroke = 283,
        /// grid-template-columns
        GridTemplateColumns = 284,
        /// grid-template-rows
        GridTemplateRows = 285,
        /// border-image-source
        BorderImageSource = 286,
        /// list-style-image
        ListStyleImage = 287,
        /// grid-auto-columns
        GridAutoColumns = 288,
        /// grid-auto-rows
        GridAutoRows = 289,
        /// fill-opacity
        FillOpacity = 290,
        /// stroke-opacity
        StrokeOpacity = 291,
        /// anchor-scope
        AnchorScope = 292,
        /// timeline-scope
        TimelineScope = 293,
        /// -moz-scrollbar-inset-block
        MozScrollbarInsetBlock = 294,
        /// -moz-scrollbar-inset-inline
        MozScrollbarInsetInline = 295,
        /// -moz-window-transform
        MozWindowTransform = 296,
        /// transform
        Transform = 297,
        /// column-width
        ColumnWidth = 298,
        /// -moz-line-scroll-amount
        MozLineScrollAmount = 299,
        /// column-gap
        ColumnGap = 300,
        /// row-gap
        RowGap = 301,
        /// -moz-box-ordinal-group
        MozBoxOrdinalGroup = 302,
        /// order
        Order = 303,
        /// -x-span
        XSpan = 304,
        /// marker-end
        MarkerEnd = 305,
        /// marker-mid
        MarkerMid = 306,
        /// marker-start
        MarkerStart = 307,
        /// contain-intrinsic-block-size
        ContainIntrinsicBlockSize = 308,
        /// contain-intrinsic-height
        ContainIntrinsicHeight = 309,
        /// contain-intrinsic-inline-size
        ContainIntrinsicInlineSize = 310,
        /// contain-intrinsic-width
        ContainIntrinsicWidth = 311,
        /// grid-column-end
        GridColumnEnd = 312,
        /// grid-column-start
        GridColumnStart = 313,
        /// grid-row-end
        GridRowEnd = 314,
        /// grid-row-start
        GridRowStart = 315,
        /// max-block-size
        MaxBlockSize = 316,
        /// max-height
        MaxHeight = 317,
        /// max-inline-size
        MaxInlineSize = 318,
        /// max-width
        MaxWidth = 319,
        /// flex-grow
        FlexGrow = 320,
        /// flex-shrink
        FlexShrink = 321,
        /// -moz-box-flex
        MozBoxFlex = 322,
        /// stroke-miterlimit
        StrokeMiterlimit = 323,
        /// cx
        Cx = 324,
        /// cy
        Cy = 325,
        /// offset-distance
        OffsetDistance = 326,
        /// x
        X = 327,
        /// y
        Y = 328,
        /// flood-opacity
        FloodOpacity = 329,
        /// -moz-window-opacity
        MozWindowOpacity = 330,
        /// opacity
        Opacity = 331,
        /// shape-image-threshold
        ShapeImageThreshold = 332,
        /// stop-opacity
        StopOpacity = 333,
        /// border-bottom-left-radius
        BorderBottomLeftRadius = 334,
        /// border-bottom-right-radius
        BorderBottomRightRadius = 335,
        /// border-end-end-radius
        BorderEndEndRadius = 336,
        /// border-end-start-radius
        BorderEndStartRadius = 337,
        /// border-start-end-radius
        BorderStartEndRadius = 338,
        /// border-start-start-radius
        BorderStartStartRadius = 339,
        /// border-top-left-radius
        BorderTopLeftRadius = 340,
        /// border-top-right-radius
        BorderTopRightRadius = 341,
        /// corner-bottom-left-shape
        CornerBottomLeftShape = 342,
        /// corner-bottom-right-shape
        CornerBottomRightShape = 343,
        /// corner-end-end-shape
        CornerEndEndShape = 344,
        /// corner-end-start-shape
        CornerEndStartShape = 345,
        /// corner-start-end-shape
        CornerStartEndShape = 346,
        /// corner-start-start-shape
        CornerStartStartShape = 347,
        /// corner-top-left-shape
        CornerTopLeftShape = 348,
        /// corner-top-right-shape
        CornerTopRightShape = 349,
        /// bottom
        Bottom = 350,
        /// inset-block-end
        InsetBlockEnd = 351,
        /// inset-block-start
        InsetBlockStart = 352,
        /// inset-inline-end
        InsetInlineEnd = 353,
        /// inset-inline-start
        InsetInlineStart = 354,
        /// left
        Left = 355,
        /// right
        Right = 356,
        /// top
        Top = 357,
        /// margin-block-end
        MarginBlockEnd = 358,
        /// margin-block-start
        MarginBlockStart = 359,
        /// margin-bottom
        MarginBottom = 360,
        /// margin-inline-end
        MarginInlineEnd = 361,
        /// margin-inline-start
        MarginInlineStart = 362,
        /// margin-left
        MarginLeft = 363,
        /// margin-right
        MarginRight = 364,
        /// margin-top
        MarginTop = 365,
        /// block-size
        BlockSize = 366,
        /// height
        Height = 367,
        /// inline-size
        InlineSize = 368,
        /// min-block-size
        MinBlockSize = 369,
        /// min-height
        MinHeight = 370,
        /// min-inline-size
        MinInlineSize = 371,
        /// min-width
        MinWidth = 372,
        /// width
        Width = 373,
        /// -moz-window-input-region-margin
        MozWindowInputRegionMargin = 374,
        /// scroll-margin-block-end
        ScrollMarginBlockEnd = 375,
        /// scroll-margin-block-start
        ScrollMarginBlockStart = 376,
        /// scroll-margin-bottom
        ScrollMarginBottom = 377,
        /// scroll-margin-inline-end
        ScrollMarginInlineEnd = 378,
        /// scroll-margin-inline-start
        ScrollMarginInlineStart = 379,
        /// scroll-margin-left
        ScrollMarginLeft = 380,
        /// scroll-margin-right
        ScrollMarginRight = 381,
        /// scroll-margin-top
        ScrollMarginTop = 382,
        /// border-block-end-width
        BorderBlockEndWidth = 383,
        /// border-block-start-width
        BorderBlockStartWidth = 384,
        /// border-bottom-width
        BorderBottomWidth = 385,
        /// border-inline-end-width
        BorderInlineEndWidth = 386,
        /// border-inline-start-width
        BorderInlineStartWidth = 387,
        /// border-left-width
        BorderLeftWidth = 388,
        /// border-right-width
        BorderRightWidth = 389,
        /// border-top-width
        BorderTopWidth = 390,
        /// column-rule-width
        ColumnRuleWidth = 391,
        /// outline-width
        OutlineWidth = 392,
        /// padding-block-end
        PaddingBlockEnd = 393,
        /// padding-block-start
        PaddingBlockStart = 394,
        /// padding-bottom
        PaddingBottom = 395,
        /// padding-inline-end
        PaddingInlineEnd = 396,
        /// padding-inline-start
        PaddingInlineStart = 397,
        /// padding-left
        PaddingLeft = 398,
        /// padding-right
        PaddingRight = 399,
        /// padding-top
        PaddingTop = 400,
        /// r
        R = 401,
        /// shape-margin
        ShapeMargin = 402,
        /// rx
        Rx = 403,
        /// ry
        Ry = 404,
        /// scroll-padding-block-end
        ScrollPaddingBlockEnd = 405,
        /// scroll-padding-block-start
        ScrollPaddingBlockStart = 406,
        /// scroll-padding-bottom
        ScrollPaddingBottom = 407,
        /// scroll-padding-inline-end
        ScrollPaddingInlineEnd = 408,
        /// scroll-padding-inline-start
        ScrollPaddingInlineStart = 409,
        /// scroll-padding-left
        ScrollPaddingLeft = 410,
        /// scroll-padding-right
        ScrollPaddingRight = 411,
        /// scroll-padding-top
        ScrollPaddingTop = 412,
        /// background-color
        BackgroundColor = 413,
        /// border-block-end-color
        BorderBlockEndColor = 414,
        /// border-block-start-color
        BorderBlockStartColor = 415,
        /// border-bottom-color
        BorderBottomColor = 416,
        /// border-inline-end-color
        BorderInlineEndColor = 417,
        /// border-inline-start-color
        BorderInlineStartColor = 418,
        /// border-left-color
        BorderLeftColor = 419,
        /// border-right-color
        BorderRightColor = 420,
        /// border-top-color
        BorderTopColor = 421,
        /// column-rule-color
        ColumnRuleColor = 422,
        /// flood-color
        FloodColor = 423,
        /// lighting-color
        LightingColor = 424,
        /// outline-color
        OutlineColor = 425,
        /// stop-color
        StopColor = 426,
        /// text-decoration-color
        TextDecorationColor = 427,
        /// text-emphasis-color
        TextEmphasisColor = 428,
        /// -webkit-text-fill-color
        WebkitTextFillColor = 429,
        /// -webkit-text-stroke-color
        WebkitTextStrokeColor = 430,
}