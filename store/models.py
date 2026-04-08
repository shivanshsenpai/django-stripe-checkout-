import uuid
from django.db import models


class Product(models.Model):
    """A product in the store catalog, seeded via management command."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f"{self.name} (${self.price})"

    @property
    def price_in_cents(self):
        """Stripe expects amounts in cents."""
        return int(self.price * 100)


class Order(models.Model):
    """
    Customer order. UUID primary key doubles as Stripe idempotency key.
    Status transitions: pending → paid (one-way, enforced in webhook).
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    stripe_session_id = models.CharField(max_length=200, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} — {self.status}"

    @property
    def total(self):
        return sum(item.price_at_purchase * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Line item — captures price at purchase time so totals survive price changes."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ ${self.price_at_purchase}"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity
