from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('checkout/', views.create_checkout, name='create_checkout'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
