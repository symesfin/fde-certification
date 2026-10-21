# Northline Broadband — Network Operations

The Network Operations Centre (NOC) is the 12-person team that runs Northline's core and access network, owns the regional service-level objectives, and approves every planned change. This page describes what the NOC measures, how it responds, and how the service desk interacts with it.

## Regions and Topology

The network is organised as three regions — North, Central and Coast — each with an aggregation point that connects the region's street cabinets to the core in the Central region. The North region is full fibre throughout. The Central region hosts the core, the head office and the primary NOC. The Coast region is a mix of full fibre and the legacy fixed-wireless service, and its aggregation point is the furthest from the core.

## Regional Latency Objectives

The NOC tracks P95 line latency per region as a core service-level objective, measured from the regional aggregation point to the core. The objective is 150 ms at peak for every region. In 2024 the North region sat around 120 ms, Central around 180 ms at peak, and the Coast region reached 240 ms, the worst of any region, which generated most of the year's alerts and the on-call pages that led to the Coast cache.

## The Coast Cache

The Coast cache is a regional content cache installed at the Coast aggregation point in autumn 2024 after a summer of latency alerts. It serves popular content from inside the region so that peak-hour traffic no longer crosses to the core, and it brought Coast P95 latency back under the objective. The cache is a planned-change asset: it is patched in the Coast maintenance window and its failure mode is slower service, not an outage.

## Alerting and On-Call

When a region exceeds its P95 latency objective at peak, or when the test head reports more than fifty ONTs in one cabinet losing signal at once, the NOC pages the on-call network engineer. The on-call engineer declares a regional incident if the cause is in the aggregation point, the cabinet or the core; individual customer tickets inside the incident area are linked to it and desk diagnosis stops.

## Planned Changes and Maintenance Windows

Every change to the network is a ticket with a NOC change approval. Each region has a weekly maintenance window — North on Tuesday, Central on Wednesday, Coast on Thursday, all from 01:00 to 05:00 — and customer-affecting changes happen only inside the window, with a notice to affected customers 48 hours in advance. A change outside the window needs the CTO's approval and a rollback plan.

## The Line Test Head

The NOC operates the automated line test head that the fault runbook relies on. A line test reports the optical receive level at the ONT, errored seconds over the last 24 hours, and the time of the last ONT reboot, and returns a line-test reference that the ticket must carry before a truck roll can be booked. The test head runs inside the network and reads only diagnostic data, never account data.

## Incident Review

Every regional incident gets a written review within five working days: timeline, impact by connections and by business customers, root cause from the fixed list, and the follow-up actions with owners. The review is shared with the service desk so that the status message customers were given can be compared with what actually happened.

## Working with the Service Desk

The desk reaches the NOC through the incident board and through network tickets raised by field engineers from site. The NOC does not take customer calls and does not see account data; a question about a customer's bill is never a NOC question, and a question about a cabinet is never a desk question.
