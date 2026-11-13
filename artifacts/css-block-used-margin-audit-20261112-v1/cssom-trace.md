# trace: `CSSOM#dom-window-getcomputedstyle` -> `CSSOM#resolved-value`

Max depth 9, kind `step`. Found 1 trace(s).

## Trace 1 (1 hop(s))

1) `CSSOM#dom-window-getcomputedstyle` step 5 calls `CSSOM#resolved-value`
   > If obj is not null, and elt is connected, part of the flat tree, and its shadow-including root has a browsing context which either doesn’t have a browsing context container, or whose browsing context container is being rendered, set decls to a list of all longhand properties that are supported CSS properties, in lexicographical order, with the value being the resolved value computed for obj using the style rules associated with doc. Additionally, append to decls all the custom properties whose computed value for obj is not the guaranteed-invalid value. There are UAs that handle shorthands, and all UAs handle shorthands that used to be longhands like overflow, see #2529. Order of custom properties is currently undefined, see #4947.

