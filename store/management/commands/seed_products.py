from django.core.management.base import BaseCommand
from store.models import Product

PRODUCTS = [
    {
        'name': 'Wireless Headphones',
        'description': 'Noise-cancelling, 30hr battery, premium sound.',
        'price': 79.99,
    },
    {
        'name': 'Smart Watch',
        'description': 'Fitness tracking, heart rate, notifications.',
        'price': 199.99,
    },
    {
        'name': 'Bluetooth Speaker',
        'description': 'Portable, waterproof, 360° surround sound.',
        'price': 49.99,
    },
    {
        'name': 'USB-C Hub',
        'description': '7-in-1 adapter, HDMI, USB 3.0, SD card.',
        'price': 34.99,
    },
    {
        'name': 'HD Webcam',
        'description': '1080p, auto-focus, built-in mic, plug & play.',
        'price': 59.99,
    },
    {
        'name': 'Phone Stand',
        'description': 'Adjustable aluminum dock, anti-slip base.',
        'price': 24.99,
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with fixed products (idempotent)'

    def handle(self, *args, **options):
        created_count = 0

        for product_data in PRODUCTS:
            _, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} created, {len(PRODUCTS) - created_count} already existed.'
        ))
