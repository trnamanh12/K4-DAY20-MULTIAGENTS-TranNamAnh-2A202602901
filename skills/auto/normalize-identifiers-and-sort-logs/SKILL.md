---
name: normalize-identifiers-and-sort-logs
description: Use when processing log files or structured event data with service names and timestamps.
---
- Normalize service names to lowercase and replace hyphens with underscores according to domain specifications.
- Sort error and event lists by service name first, then by UTC timestamp in ascending order.
