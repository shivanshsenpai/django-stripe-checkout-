# AI Assist Disclosure

## Tools Used

| Tool | Usage |
|------|-------|
| **AI Coding Assistant** | Used for frontend styling and layout |

## Where AI Was Used

### Frontend (HTML/CSS)
- AI assisted with the Bootstrap 5 layout and custom CSS styling
- Dark theme design, animations, and responsive layout were generated with AI help
- I reviewed and adjusted colors, spacing, and overall UX

## What Was NOT AI-Generated
- **Backend logic** — Django views, models, URL routing, Stripe integration
- **Architecture decisions** — Stripe Checkout over Payment Intents, UUID-as-idempotency-key
- **Double-charge prevention** — Three-layer approach (idempotency key, status state machine, client-side disable)
- **Database design** — Product, Order, OrderItem schema with price snapshots
- **Webhook handler** — Signature verification and idempotent order updates
- **Testing & debugging** — All end-to-end testing done manually
