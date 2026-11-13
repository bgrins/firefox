# Initial clamp diagnostic repair — source review checkpoint

Root accepted this exact diff for local validation. Before/after snapshots preserve the three-path change; PROTECTED pins all seven existing chrome tests and the native header/DOM implementation, including existing dirty content.

Freeze timing is unchanged because automatic content measurement consults IsFrozen for forceBResize. Only classification moves after automatic basis/minimum resolution and reads the final item fields. The normal constructor starts unfrozen; the only freeze before this point is the inflexible branch, and Freeze clears both flags. Automatic basis/minimum resolution does not set them. Flexible items retain their old resolver classification path. No used/base size assignment is added.

The 36-case regression has108 assertions (used size, resolved base, clamp state) across row/column/column-reverse, measured auto/explicit basis, flexible/inflexible, min/max/equality/no-max, and aspect ratio. Chrome is required because FlexItemValues is ChromeOnly; normal WPT cannot observe diagnostic clampState, while rendered sizes already pass. Existing tests remain untouched.

Eight isolated patch checks/applications/reversals passed against exact dirty preimage and HEAD5fcf976eeb79ddc057e9c73d7b73a422058b1903; scratch was removed. No Git index/commit changed. Root authorized finaltest baseline before rebuild, bounded2job existing-objdir build, focused and full dom/flex chrome validation. Results remain pending at this checkpoint.
