from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('premium_upgrade/', views.premium_upgrade, name='premium_upgrade'),
    path('payment_successful/', views.payment_successful, name='payment_successful'),
    path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)