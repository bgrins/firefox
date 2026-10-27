# Remaining image and XUL caller domain

The two residual shipped-frame paths do not provide an identified route to the exceptional default-First, inverted, margin-synthesis query. This completes the bounded source classification from `css-central-baseline-caller-exclusion-v1`; it is not a whole-program proof over arbitrary frame trees or privileged mutations. All source statements below refer to explicit revision `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`, not the transient working tree or a moving HEAD.

## Image UA shadow roots

`nsImageFrame::IsLeafDynamic` is genuinely conditional: ordinary image-loading content with a UA shadow root is non-leaf. It would be incorrect to exclude this by asserting all image frames are leaves. Frames created for `content: url()` remain leaves even when their element has an author shadow root.

No image widget producer appears in `UAWidgetsChild::setupWidget`: its supported names are video/audio, input and marquee. `Element::AttachShadow` checks `CanAttachShadowDOM`; `nsContentUtils::IsValidShadowHostName` excludes img. The ordinary author API therefore cannot put bare text in an image shadow root. `ShadowRoot.setIsUAWidget` is ChromeOnly. The anonymous-content API creates its own div host, not an image. Cloning an existing UA root preserves its flag/content; it does not originate an author-created image root.

The generic producer requiring special attention is `nsXMLPrettyPrinter::PrettyPrint`. It attaches a UA root to the document element and appends the result of the fixed XMLPrettyPrint stylesheet. This is not an ordinary image-root route: `nsXMLContentSink::CreateElement` marks XHTML as factored; `HasElementCreator` marks XUL, SVG and MathML as factored too. `CanStillPrettyPrint` rejects factored documents unless the document root is the specifically recognized XSLT stylesheet/transform. That exception is not an HTML img or XUL image root. Root replacement also fails the identity check in `MaybePrettyPrint`.

Even considered independently of that admission guard, the printer's root template emits exactly one literal XHTML `div#top`. Author XML text is rendered by `value-of` within the generated descendants, not appended as a bare shadow-root child. The fixed stylesheet does not use disable-output-escaping. HTML UA CSS makes the outer div block; XMLPrettyPrint.css and its viewsource.css import do not turn it into display:contents. Thus the generic producer provides an element/block boundary rather than a direct author text child of an image frame. The XML template structure was checked mechanically without running XSLT.

These facts exclude the identified normal author/shipped-widget routes. They do not promise that privileged code cannot manufacture a UA root or replace its children, nor that a future image widget will preserve the same frame shape.

## XUL labels and textboxes

`FindXULTagData` has no native textbox-specific entry. Ordinary XUL elements use CSS display; xul.css defaults them to flex. Bare text in a flex container receives the anonymous block already audited in `CreateNeededAnonFlexOrGridItems`. A generic textbox element therefore is not evidence of a legacy direct nsTextBoxFrame parent.

The actual shipped editable examples are HTML inputs: AutocompleteInput extends HTMLInputElement and registers with extends:input; findbar's textbox markup is an html:input inside a wrapper. `nsTextControlFrame` derives ScrollContainerFrame and explicitly returns Last from `GetDefaultBaselineSharingGroup`. Its fallback path is already separately classified in the preceding caller audit.

Ordinary XUL label CSS is inline-block, and description is flow-root, yielding block containers. The special `value` plus `crop=center` path in `FindLabelOrDescriptionData` creates MiddleCroppingLabelFrame. That class derives MiddleCroppingBlockFrame, which derives nsBlockFrame. `CreateAnonymousContent` does create a direct anonymous text node, but its frame parent is consequently a block with default Last, not a default-First exceptional provider. The special constructor does not apply without ChromeRulesEnabled, value and center cropping; those cases follow CSS display. CSS flex/grid alternatives retain the anonymous-block argument; an out-of-flow ordinary inline is blockified as covered by the preceding audit.

For the precise orthogonal query, `nsTextFrame::GetNaturalBaselineBOffset` asks its immediate parent's `GetLogicalBaseline(aWM)` without a group argument. That overload uses the parent's default group, not the text's baseline-source property. An ancestor outer widget or an out-of-flow margin owner is therefore not substituted for these intervening block/scroll parents.

## Scoped range conclusion

Together with the preceding domain and caller reports, no reachable counterexample to the new subtraction has been identified in these well-formed shipped construction paths. For normal style margins and the audited in-flow used-margin producers, the opposite margin lower bound supports the compiled arithmetic theorem. The known cached negative-auto-margin exception is out-of-flow; its identified direct/indirect query routes either exclude the provider, use default Last, or use a different fallback box.

This remains a source argument plus conditional arithmetic proofs. Its scope assumes completed well-formed layout, nonnegative frame extents, and defined pre-existing operations. It excludes malformed/native-injected frame trees, arbitrary privileged UA-shadow mutation, intermediate construction/destruction states and prior signed-overflow states. It does not establish safety for every possible nsIFrame implementation, close unrelated old synthesis arithmetic issues, or justify a clamp/legacy-raw fallback. No additional native patch, browser result or accepted bug is claimed here.
