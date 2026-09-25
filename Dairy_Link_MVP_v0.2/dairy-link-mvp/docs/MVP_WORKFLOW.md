# Dairy Link MVP Workflow

1. Register farmer with unique Farmer ID (max 10 characters).
2. Register one or more animals against the farmer.
3. Capture milk for the farmer by date and morning/evening session.
4. View weekly milk totals.
5. Calculate weekly gross milk value using a configurable price per litre.
6. Record a payment and payment method/reference.
7. View farmer payment history and dashboard totals.

The system currently stores records in PostgreSQL. Production development should
add authentication, authorization, validation, audit logs, offline sync,
database migrations and payment-provider integration before deployment.
