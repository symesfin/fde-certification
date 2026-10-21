# Northline Broadband — Customer Data Handling

Northline Broadband holds personal data for around 180,000 connections: names, addresses, account references, payment details, call recordings, and the diagnostic data that modems and the network produce. This page defines how that data is protected throughout its lifecycle and what the service desk, field engineering and the NOC are required to do. It applies to every system that touches customer data, including the diagnostics assistant piloted on the second-line desk.

## Data Encryption at Rest and in Transit

All customer data is encrypted at rest using AES-256 with keys held in a managed key service; keys rotate on a 90-day cycle and key access is logged. Data in transit is protected with TLS 1.2 or higher on every internal and external path, including the link between the service desk tools and the ticket system and the link from the NOC test head to the ONT management interface. Database volumes, object storage, call-recording archives and backup snapshots are encrypted by default. Payment card details are never stored by Northline; they are tokenised by the payment gateway under PCI DSS.

## Access Control and Least Privilege

Access to customer data is role-based and follows least privilege. First-line agents see the account, the tariff and open tickets for the customer they are speaking to; second-line engineers additionally see line-test results and modem diagnostics; the NOC sees network data but not account or payment details. Privileged access requires multi-factor authentication and is reviewed quarterly. Every read of a customer record is logged with the agent identity, and the log is immutable. Joiner-mover-leaver workflows provision, adjust and revoke access on the day of the change.

## Customer Data Must Stay Inside the Network

Customer data — including a screenshot of a modem status page, which carries the account reference — may not be sent to any system outside the Northline network. Any tool that reads tickets, screenshots or call recordings runs inside the network or does not run. A request to use an external service for customer data is a change request to Security, not a desk decision.

## Call Recordings

Every support call is recorded. Recordings are retained for 24 months, are searchable only by ticket reference, and are paused automatically during card payment under PCI DSS. A customer may request their recordings under data-protection law; the request is fulfilled by the Data Protection Officer within 30 days. Recordings may be used for training and quality review only after the customer's identifiers are removed.

## Data Retention and Deletion

Account data is retained for the life of the account plus six years for financial records. Diagnostic data from modems and the network is retained for 90 days unless attached to an open ticket. Call recordings are retained for 24 months. Deletion is automatic at the end of each period, is logged, and is suspended for any record under a legal hold.

## Legal Hold Procedure

A record under a legal hold carries an `LH-` reference on the account and on every linked ticket. Records under legal hold may not be summarised, edited, exported or distributed, and must not be processed by any automated tool, including the diagnostics assistant. A desk agent who finds a legal hold reference stops work on the record and routes the request to Legal and Security. The hold is lifted only by Legal.

## Incident Response and Breach Notification

A suspected data breach is reported to Security within one hour of discovery. Security triages within four hours, and where personal data is affected the Data Protection Officer notifies the regulator within 72 hours and affected customers without undue delay. The March billing incident, in which a cohort was double-charged, was handled as a financial incident rather than a data breach because no data left the network; the distinction is Security's to make, not the desk's.

## Diagnostic Data and the Diagnostics Assistant

The diagnostics assistant reads ticket text, modem status screenshots and runbooks to suggest a diagnosis to a second-line engineer. It runs inside the network, is barred from any record under legal hold, and must cite the ticket, line-test reference or runbook section it relied on. A diagnosis it suggests is a suggestion; the engineer records the root cause.

## Supplier and Sub-Processor Management

Suppliers that process customer data — the payment gateway, the mobile carrier, the call-recording platform — are listed on the sub-processor register, hold a signed data-processing agreement, and are reviewed annually. A new supplier that would process customer data cannot be used until it is on the register.

## Employee Security Training

All staff complete data-handling training at induction and annually. Field engineers additionally complete training on handling customer premises and on the rule that a photograph taken at a customer's premises is customer data and is stored only in the ticket.
