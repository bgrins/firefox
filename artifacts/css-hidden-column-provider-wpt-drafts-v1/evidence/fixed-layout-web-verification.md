# Direct primary fallback

The web tool opened https://www.w3.org/TR/CSS22/tables.html#fixed-table-layout successfully after the local index reported its fragment unavailable (both failures retained). Section17.5.2.1 specifies that unspecified fixed-layout columns divide remaining table space equally. This motivates the three equal empty tracks; the fixture independently checks every visible cell rectangle before any hidden-query result is accepted. It does not use this rule to infer col/span DOM rectangle multiplicity.
