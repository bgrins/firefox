# Paused registered-length animation review

Bounded independent review found no concrete oracle or timing blocker. Six cases cover absolute, font-relative and selected absolute var() endpoints at ancestor zoom1/2. Local zoom visits1/2/.5/1.5/1 at font20 then30; a final commitStyles()+cancel snapshot tests retained computed length.

[Setting current time](https://drafts.csswg.org/web-animations-1/#setting-the-current-time-of-an-animation) completes a pending pause synchronously. The setup therefore needs no ready-promise wait after pause()+currentTime500. Explicit currentTime500 and progress0.5 assertions now verify this precondition.

[Computed keyframes](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes) are recalculated for the current target context when evaluating an effect. Font-relative endpoints therefore yield40px and60px midpoints at font20px and30px. [Registered animation behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior-of-custom-properties) interpolates these admitted lengths by computed value. The ready unregistered endpoint providers select10px/30px; their unused em fallbacks do not participate.

[commitStyles](https://drafts.csswg.org/web-animations-1/#dom-animation-commitstyles) persists current computed effect values. Canceling afterward should retain the final midpoint. The fixture does not mutate font or zoom after commitment and therefore does not claim to test all post-commit recomputation boundaries. A nonunit ancestor still exercises effective zoom at the committed snapshot.

Canonical CSSOM/consumer dimensions and multiplicative geometry expectations match the existing zoom draft's coordinate model. Height10px is an independent geometry calibration. No transforms, borders, padding, percentage resolution or active timing progress affect the expected widths.

Frozen HTML SHA 662e6fee6ae89a66e88331855b811d9995d771d13f303ab51f20cba068f08e0f. Final JS syntax and six unique test registrations passed60a097/0; the temporary directory was removed. Test callbacks and browser execution have not occurred. This source review does not accept a native fix or add coverage credit.

V2 corrects the API help fragment only. Official captured DOM IDs verify the API and WA1 anchors; static syntax passed7417e6/0. Test bodies and names are byte-identical to v1.
