# Northline Broadband — Glossary, Codes & Standards

This reference catalogues the acronyms, status codes, product codes and standards used across Northline Broadband's service desk, field engineering and NOC. Entries are maintained by Knowledge Operations and are the wording to quote in ticket notes and customer-facing messages. When a code in a ticket is not in this glossary, the ticket note should say so rather than expand it from memory.

## LOS — Loss of Signal

`LOS` stands for Loss of Signal. On a fibre connection it means the optical network terminal (ONT) is receiving no light, or light below the receive threshold, from the street cabinet. A LOS condition is shown on the customer's modem status page as a red LOS light and, on current firmware, as a hexadecimal sub-code (see `LOS 0x21` and `LOS 0x2A`). LOS is never a customer-equipment fault on its own; it is diagnosed from the line-test result and routes to the fault runbook's line stage.

## LOS 0x21 — Optical Level Below Threshold

`LOS 0x21` is the LOS sub-code for optical receive power below threshold at the ONT. It usually indicates a bent or damaged fibre drop, a dirty connector, or a splitter fault in the street cabinet. A ticket carrying `LOS 0x21` requires a line test before any customer-equipment step; a modem swap does not clear it.

## LOS 0x2A — No Optical Signal

`LOS 0x2A` is the LOS sub-code for no optical signal at all. It most often means a cut drop cable or a cabinet-side disconnection and is treated as a probable truck roll from the first diagnosis. The code is easy to misread as `0x21` on a photographed screen; the runbook requires the code to be confirmed from the line test, not from the screenshot.

## ONT — Optical Network Terminal

`ONT` stands for Optical Network Terminal, the device that converts the fibre signal into Ethernet for the customer's router. Northline supplies the ONT and it remains Northline's property; the router is customer premises equipment (CPE) and may be Northline-supplied or the customer's own.

## CPE — Customer Premises Equipment

`CPE` stands for Customer Premises Equipment: the router, mesh units, phone adapter and any other device in the customer's home. CPE faults are the single largest ticket root cause, which is why the fault runbook's first stage is a guided CPE check before any line work.

## FTR — First-Time Resolution

`FTR` stands for first-time resolution, the share of tickets closed on the first contact without a callback, a repeat ticket within seven days, or a truck roll. It is the headline service-desk metric. A ticket re-opened within seven days is counted against FTR for the agent who closed it.

## TTR — Time to Restore

`TTR` stands for time to restore, measured from the ticket being opened to service being confirmed working by the customer. The Fibre Business tariffs carry a TTR commitment with service credits; the residential tariffs carry a target only.

## NOC — Network Operations Centre

`NOC` stands for Network Operations Centre, the 12-person team that monitors the core and access network, owns the regional latency objectives, and approves planned changes. The NOC pages the on-call network engineer when a region exceeds its P95 latency target at peak.

## NL-F150-12 — Fibre 150 Home

`NL-F150-12` is the product code for the Fibre 150 Home tariff: 150 Mbps full fibre, residential, twelve-month minimum term. See the tariffs page for pricing and terms.

## NL-F500-24 — Fibre 500 Home

`NL-F500-24` is the product code for the Fibre 500 Home tariff: 500 Mbps full fibre, residential, twenty-four-month minimum term. The most commonly sold residential tariff.

## NL-F1000-36 — Fibre 1000 Business

`NL-F1000-36` is the product code for the Fibre 1000 Business tariff: symmetric 1 Gbps full fibre with a TTR commitment, thirty-six-month minimum term.

## LH — Legal Hold Reference

`LH-` followed by a number is a legal hold reference. A ticket, call recording or record marked with a legal hold reference may not be summarised, edited or distributed; questions about it are routed to Legal and Security. The data-handling page describes the procedure.

## PCI DSS

`PCI DSS` is the payment card industry security standard that governs how Northline handles card details taken over the phone. Agents never type a card number into a ticket; payments are taken through the payment gateway's agent-assist line, and call recording is paused during card entry.

## Internal Shorthand

`truck roll` — booking a field engineer visit. `line test` — the automated optical and copper test run from the NOC's test head. `swap-by-post` — sending a replacement router without a visit. `save desk` — the retention team that handles cancellation requests. `the Coast cache` — the regional content cache installed at the Coast aggregation point in 2024.
