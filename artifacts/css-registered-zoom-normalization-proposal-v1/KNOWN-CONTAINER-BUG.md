Source: https://bugzilla.mozilla.org/show_bug.cgi?id=1894104
Fetched through moz.get_bugzilla_bug during this investigation.

# Bug 1894104 - Fix interaction of zoom and container query units.

## Basic Information
- **Status**: NEW
- **Severity**: S3
- **Product**: Core
- **Component**: CSS Parsing and Computation
- **Version**: unspecified
- **Platform**: Unspecified
- **OS**: Unspecified
- **Created**: 2024-04-29T21:12:57Z
- **Last Updated**: 2024-04-30T01:59:52Z
- **Related URL**: https://github.com/w3c/csswg-drafts/issues/10268

## People Involved
- **Reporter**: Emilio Cobos Álvarez [:emilio] (emilio@crisal.io)
- **Assignee**: Nobody; OK to take it and work on it (nobody@mozilla.org)
- **CC Count**: 1 people

## Bug Relationships
- **Depends on**: 390936, 1892676

## Bug Timeline

**2024-04-29 21:12:57** - Comment #0 by emilio@crisal.io
Much like bug 1892676, container query units need some special handling for zoom since the container query sizes are in unzoomed CSS pixels.

https://github.com/w3c/csswg-drafts/issues/10268 has a description of the issues, for now not touching it.

