# Django Stripe Checkout — VipraTech Assignment

A Django web application that displays fixed products, allows quantity selection, processes payments via Stripe Checkout (test mode), and displays paid orders.

---

## Assumptions

1. **No user authentication** — Orders are not tied to specific users. In production, Django's auth would scope orders per user.
2. **Fixed product catalog** — Products are seeded via management command.
3. **USD currency** — All prices in US dollars.
4. **SQLite for local dev** — Schema is Postgres-compatible (UUID fields, decimal types). Switching requires only a `DATABASE_URL` change.
5. **Stripe test mode** — Uses test API keys, no real charges.

---

## Flow: Stripe Checkout Sessions

**Why Checkout over Payment Intents?**

| Criteria | Stripe Checkout | Payment Intents |
|----------|----------------|--------------------|
| Complexity | Low — Stripe hosts the page | High — custom form needed |
| PCI Compliance | Built-in | Requires Stripe.js |
| 3D Secure | Automatic | Manual handling |
| Best for | Simple purchases | Complex payment UX |

**Flow:**
```
User selects quantities → POST /checkout/ → Create Order (pending) + Stripe Session
→ Redirect to Stripe → User pays → Stripe redirects to /success/
→ Webhook marks order as PAID → User sees order in "My Orders"
```

---

## Double Charge Prevention

### 1. Idempotency Key
Each `Order` uses a UUID primary key, passed as `idempotency_key` to Stripe. Retries return the same session.

### 2. Status State Machine
Orders follow `pending → paid` (one-way). The webhook only transitions if currently `pending` — already-paid orders are skipped.

### 3. Client-side + PRG Pattern
- Buy button disabled after click (prevents double-click)
- POST-Redirect-GET pattern prevents form resubmission on refresh
- Success URL does a GET redirect to the main page

---

## Setup

### Prerequisites
- Python 3.10+
- [Stripe account](https://dashboard.stripe.com/register) (free, test mode)

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/django-stripe-checkout.git
cd django-stripe-checkout
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` with your Stripe test keys from https://dashboard.stripe.com/test/apikeys

### 3. Initialize Database
```bash
python manage.py migrate
python manage.py seed_products
```

### 4. Run
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000

### 5. Webhook (optional, for local dev)
```bash
stripe listen --forward-to localhost:8000/webhook/
```
Copy the `whsec_...` secret to your `.env` file.

### Test Cards
| Card | Result |
|------|--------|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 0002` | Declined |
| Any future expiry, any 3-digit CVC |

---

## Project Structure

```
django-stripe-checkout/
├── config/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                    # Main app
│   ├── management/commands/
│   │   └── seed_products.py  # Product seeder
│   ├── static/store/css/
│   │   └── style.css         # All custom styles
│   ├── templates/store/
│   │   └── index.html        # Main page (Bootstrap 5)
│   ├── admin.py
│   ├── models.py             # Product, Order, OrderItem
│   ├── urls.py
│   └── views.py              # Checkout, webhook, success
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── AI-assist.md
```

---

## Code Quality Notes

- **Idempotent operations** — Seed command uses `get_or_create`, webhook checks status before updating
- **Price snapshots** — `OrderItem.price_at_purchase` captures price at checkout time
- **Separation of concerns** — Models handle data, views handle flow, CSS is a separate static file
- **Django best practices** — `app_name` namespacing, `related_name` on FKs, `PROTECT` on product FK, `update_fields` on saves
- **Security** — CSRF on forms, webhook signature verification, secrets in env vars

---

## Time Spent

| Phase | Time |
|-------|------|
| Planning & architecture | ~20 min |
| Models & DB design | ~15 min |
| Views & Stripe integration | ~30 min |
| Template & styling | ~25 min |
| Documentation | ~15 min |
| Testing & debugging | ~15 min |
| **Total** | **~2 hours** |
