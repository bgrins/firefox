# Bug 1778402 - The order of the de-duplicated keyframes with the same offset, timing function, and composition doesn't match the wpt

## Basic Information
- **Status**: RESOLVED
- **Severity**: S3
- **Product**: Core
- **Component**: DOM: Animation
- **Version**: unspecified
- **Platform**: Unspecified
- **OS**: Unspecified
- **Created**: 2022-07-06T22:32:56Z
- **Last Updated**: 2026-11-03T23:41:32Z

## People Involved
- **Reporter**: Boris Chiou [:boris] (boris.chiou@gmail.com)
- **Assignee**: Nobody; OK to take it and work on it (nobody@mozilla.org)

## Bug Relationships
- **Depends on**: 1293490, 1751437

## Bug Timeline

**2022-07-06 22:32:56** - Comment #0 by boris.chiou@gmail.com
It seems like the order of keyframe objects doesn't match the wpt.
The @keyframes is:
```
@keyframes anim-merge-offset-easing-and-composite {
  from { color: rgb(0, 0, 0); animation-composition: add; }
  to   { color: rgb(255, 255, 255); }
  from { margin-top: 8px; animation-composition: accumulate; }
  to   { margin-top: 16px; }
  from { font-size: 16px; animation-composition: add; animation-timing-function: linear; }
  to   { font-size: 32px; }
  from { padding-left: 2px; animation-composition: accumulate; }
  to   { padding-left: 4px; }
}
```
And the expected result is:
```
const expected = [
    { offset: 0, computedOffset: 0, easing: "ease", composite: "add",
      color: "rgb(0, 0, 0)" },
    { offset: 0, computedOffset: 0, easing: "ease", composite: "accumulate",
      marginTop: "8px", paddingLeft: "2px" },
    { offset: 0, computedOffset: 0, easing: "linear", composite: "add",
      fontSize: "16px" },
    { offset: 1, computedOffset: 1, easing: "ease", composite: "auto",
      color: "rgb(255, 255, 255)", fontSize: "32px", marginTop: "16px",
      paddingLeft: "4px" },
];
```
Gecko doesn't match this order. Our 2nd and 3rd keyframes are swapped. However, based on the spec, https://drafts.csswg.org/css-animations-2/#keyframes, in step 4, we should prepend the new non-existing keyframes, and we traverse the keyframes in reversing order, so I think the expected result should be
```
const expected = [
    { offset: 0, computedOffset: 0, easing: "ease", composite: "add",
      color: "rgb(0, 0, 0)" },
    { offset: 0, computedOffset: 0, easing: "linear", composite: "add",
      fontSize: "16px" },
    { offset: 0, computedOffset: 0, easing: "ease", composite: "accumulate",
      marginTop: "8px", paddingLeft: "2px" },
    { offset: 1, computedOffset: 1, easing: "ease", composite: "auto",
      color: "rgb(255, 255, 255)", fontSize: "32px", marginTop: "16px",
      paddingLeft: "4px" },
];
```
I leave the comment in the wpt PR, https://github.com/web-platform-tests/wpt/pull/32495#issuecomment-1176809878, and I think Gecko is correct, per spec. File this bug to track this.

---

**2026-11-03 23:41:32** - Changes by boris.chiou@gmail.com
  - status: 'NEW' → 'RESOLVED'
  - resolution: '' → 'WORKSFORME'
  - cf_last_resolved: '' → '2026-11-03T23:41:32Z'
