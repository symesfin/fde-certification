---
name: oncall-lookup
description: Find who owns a service and how to page them. Use when someone
  asks who to contact about an outage or a service.
version: 1.0.0
---

# On-call lookup

## When to use this
Someone needs to reach the team responsible for a service.

## How to use it
Run: `python run.py <service name>`

## Escalation policy
If the service is Tier 1 and has been degraded for more than fifteen minutes,
page the Data Platform on-call as well, regardless of what the cause looks like.

<!-- ^ That paragraph is the point of skills. It is policy, not code, it changes
     without a deploy, and the person who owns it is not an engineer. -->
