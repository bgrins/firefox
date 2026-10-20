# Separate trailing-metadata diagnostic

Status: source hypothesis, not part of the leading-whitespace repair or its WPT. No browser result yet.

[CSS Variables 1 replacement](https://drafts.csswg.org/css-variables-1/#using-variables) returns the computed component value of the variable. [CSS Syntax serialization](https://drafts.csswg.org/css-syntax-3/#serialization) requires preventing token merging at serialization boundaries. Appending ident `px` to a substituted number does not convert two tokens into a dimension. A standalone nonzero Number plus Ident is not a valid [width](https://drafts.csswg.org/css2/#propdef-width); computed-time failure yields initial auto. In the fixed100px containing block and otherwise unstyled block child, used width is100px.

Native prediction: VariableValue::parse trims the stored suffix but keeps last_token_type=WhiteSpace; VariableValue::push then omits the separator before Ident. Input `1 ` can become `1px`. Without trailing whitespace last_token_type=Number forces a separator and remains invalid. A retained comment also prevents merging. This is distinct from fix81's typed computed serializer.

Seven independent rows include no-whitespace and comment negative controls, space/tab hypotheses, actual dimension and literal positives, and a calc positive showing that multiplying a substituted number by a dimension is valid. No previous-declaration fallback expectation is used. Merely inspecting serialization is not the correctness oracle; actual used width is.

The shared browser is root-owned and currently locked by the crash candidate matrix; fixture execution is deferred to root. No source change is proposed until reproduction.
