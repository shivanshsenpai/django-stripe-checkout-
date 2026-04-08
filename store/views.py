import stripe
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Order, OrderItem, Product

stripe.api_key = settings.STRIPE_SECRET_KEY


@require_GET
def index(request):
    """Main page: product catalog + paid orders list."""
    products = Product.objects.all()
    paid_orders = Order.objects.filter(
        status=Order.Status.PAID
    ).prefetch_related('items__product')

    return render(request, 'store/index.html', {
        'products': products,
        'paid_orders': paid_orders,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_POST
def create_checkout(request):
    """
    Validate quantities, create Order + OrderItems (status=pending),
    then create a Stripe Checkout Session and redirect to Stripe.
    Uses the Order UUID as idempotency_key to prevent duplicate sessions.
    """
    products = Product.objects.all()
    line_items = []
    order_items_data = []

    for product in products:
        qty_str = request.POST.get(f'quantity_{product.id}', '0')
        try:
            qty = int(qty_str)
        except (ValueError, TypeError):
            qty = 0

        if qty > 0:
            order_items_data.append({
                'product': product,
                'quantity': qty,
                'price_at_purchase': product.price,
            })
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                        'description': product.description or product.name,
                    },
                    'unit_amount': product.price_in_cents,
                },
                'quantity': qty,
            })

    if not order_items_data:
        messages.warning(request, 'Please select at least one product.')
        return redirect('store:index')

    order = Order.objects.create(status=Order.Status.PENDING)

    for item_data in order_items_data:
        OrderItem.objects.create(
            order=order,
            product=item_data['product'],
            quantity=item_data['quantity'],
            price_at_purchase=item_data['price_at_purchase'],
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            metadata={'order_id': str(order.id)},
            success_url=request.build_absolute_uri('/success/') + f'?order_id={order.id}',
            cancel_url=request.build_absolute_uri('/'),
            idempotency_key=str(order.id),
        )
    except stripe.error.StripeError as e:
        order.delete()
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('store:index')

    order.stripe_session_id = checkout_session.id
    order.save(update_fields=['stripe_session_id'])

    return redirect(checkout_session.url)


@require_GET
def checkout_success(request):
    """
    Landing after Stripe redirect. Verifies payment via Stripe API as a
    fallback (webhook is the authoritative confirmation), then redirects
    to the main page with a success message.
    """
    order_id = request.GET.get('order_id')

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if order.status == Order.Status.PENDING and order.stripe_session_id:
                try:
                    session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                    if session.payment_status == 'paid':
                        order.status = Order.Status.PAID
                        order.save(update_fields=['status', 'updated_at'])
                except stripe.error.StripeError:
                    pass
        except Order.DoesNotExist:
            pass

    messages.success(request, '🎉 Payment successful! Your order has been placed.')
    return redirect('store:index')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe webhook for checkout.session.completed.
    Verifies signature, then transitions order from pending → paid (idempotent).
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                if order.status == Order.Status.PENDING:
                    order.status = Order.Status.PAID
                    order.stripe_session_id = session.get('id', order.stripe_session_id)
                    order.save(update_fields=['status', 'stripe_session_id', 'updated_at'])
            except Order.DoesNotExist:
                return HttpResponse(status=404)

    return HttpResponse(status=200)
