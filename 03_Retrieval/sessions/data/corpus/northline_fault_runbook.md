# Northline Broadband — Fault Runbook

This is the procedure a second-line engineer follows from the moment a broadband fault ticket reaches them to the moment it is closed. The stages are in order and each one names what must be true before the next begins. A ticket note should say which stage it is at. Shortcuts are the main cause of repeat tickets and are counted against first-time resolution.

## Stage 1 — Ticket Intake and Classification

1. Confirm the ticket has the customer's account reference, the service address, and the tariff product code.
2. Classify the fault: no service, intermittent, slow, or quality (phone, TV, mobile). Mobile faults route to the NOC for the carrier.
3. Check for a legal hold reference on the account. If one is present, stop and route to Legal and Security per the data-handling page.
4. Check the NOC incident board. If the address is inside a known regional incident, link the ticket to the incident and do not diagnose individually.

## Stage 2 — Guided Customer Equipment Check

1. Walk the customer through the guided reset in the app or by phone: power-cycle the ONT and the router in that order, wait two minutes, and read back the status lights.
2. Record the lights and any status code exactly as read. A code read from a screenshot must be confirmed by the line test in Stage 3 before it is acted on.
3. If the fault clears, close the ticket with the customer on the line and note the root cause as customer equipment.
4. If the router is more than three years old and the fault is intermittent or slow, offer swap-by-post before any line work. Swap-by-post needs no approval.

## Stage 3 — Line Test

1. Run the automated line test from the NOC test head. It reports optical receive level at the ONT, errored seconds over the last 24 hours, and the last ONT reboot.
2. Compare the line test with the status code recorded in Stage 2. A `LOS 0x21` with optical level below threshold is a line fault; a `LOS 0x2A` with no optical signal is a probable cut; a clean line test with a customer-reported LOS light is a customer-equipment fault and returns to Stage 2.
3. Record the line-test reference in the ticket. A ticket cannot proceed to Stage 4 without one.

## Stage 4 — Truck Roll Approval

A truck roll is a field engineer visit, and it is the most expensive thing the desk can do. Before a truck roll is booked, all of the following prerequisites must be recorded in the ticket:

1. A completed Stage 2 guided customer equipment check, with the status lights and code recorded.
2. A line-test reference from Stage 3 that is consistent with a line fault.
3. Confirmation that the address is not inside an open regional incident on the NOC board.
4. For residential tariffs, approval from the second-line team lead. For Fibre Business tariffs, approval is automatic once items 1–3 are present, because the time-to-restore commitment is running.
5. A confirmed appointment window agreed with the customer, and a note of who will be present.
6. Access notes where they apply: a gate code, a concierge, a locked riser cupboard, a dog, or a customer who needs the visit announced by text rather than by phone. Field engineers do not carry keys and will not enter a property with nobody present, so a missing access note is a wasted visit in the making.
7. The parts expectation from the line test: a drop-cable repair needs the standard kit, a connector fault needs a cleaning kit and a spare pigtail, and a suspected splitter fault needs the cabinet key for that region, which is signed out from the depot the day before.
8. Contact on the day: the customer's preferred contact number, and the engineer's arrival-call commitment — a call 30 minutes before arrival, and a second call if the engineer will be more than 15 minutes late. A visit with no arrival call that finds nobody home is charged to the desk, not to field engineering.

Without items 1–4 the booking system rejects the truck roll regardless of how the fault looks. A truck roll booked on a screenshot code alone, without a line-test reference, is the most common cause of a wasted visit. A truck roll booked without item 8 is the second.

## Stage 5 — Engineer Visit

1. The field engineer confirms the line-test finding on site with a light meter at the ONT and at the cabinet.
2. If the fault is in the drop cable or the connector, it is repaired on the visit. If the fault is in the cabinet splitter or upstream, the engineer raises a network ticket to the NOC and the customer ticket is linked to it.
3. The engineer records the on-site reading and the repair in the ticket before leaving the premises.

## Stage 6 — Closure and Follow-Up

1. Service is confirmed working with the customer, by a speed test on the customer's device where possible.
2. The root cause is recorded from the fixed list: customer equipment, line fault, cabinet, core, billing, other.
3. Business tickets have time to restore calculated and any service credit applied on closure.
4. A ticket re-opened within seven days is reassigned to the engineer who closed it and counts against first-time resolution.

## Line Migration (Fixed Wireless to Fibre)

Coast-region customers on the legacy fixed-wireless service are migrated to fibre street by street. A migration is a planned change, not a fault: it needs a NOC change approval, a confirmed install appointment, and the customer's consent to the new tariff and minimum term before the fixed-wireless service is ceased. The fixed-wireless service must not be ceased before the fibre service is confirmed working from the customer's premises.

## Incident Handling During a Regional Outage

When the NOC declares a regional incident, individual diagnosis stops for addresses inside the incident area. Tickets are linked to the incident, customers receive the incident status message, and time to restore for business tickets is measured from the incident's declared start. Truck rolls inside an incident area are suspended until the NOC clears them.
