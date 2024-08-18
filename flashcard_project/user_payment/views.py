import stripe
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decouple import config
from .models import UserPayment
from flashcard_app.models import Profile

# Set Stripe API key
stripe.api_key = config('STRIPE_SECRET_KEY')

# View to handle premium upgrade
@login_required
def premium_upgrade(request):
    if request.method == 'POST':
        try:
            # Create a Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': config('STRIPE_PRICE_ID'),  
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('payment_successful') + "?session_id={CHECKOUT_SESSION_ID}"),
                cancel_url=request.build_absolute_uri(reverse('payment_cancelled')),
                customer_creation='always',
            )

            return redirect(session.url, code=303)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('premium_upgrade')

    return render(request, 'premium_upgrade.html')

# View to handle successful payments
def payment_successful(request):
    checkout_session_id = request.GET.get('session_id', None)
    if not checkout_session_id:
        messages.error(request, "No payment session found.")
        return redirect('premium_upgrade')
    
    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer = stripe.Customer.retrieve(session.customer)

        # Update the UserPayment checkout session id
        user = request.user
        user_payment = UserPayment.objects.get(user=user)
        user_payment.stripe_checkout_id = checkout_session_id
        user_payment.save()

        messages.success(request, "Your payment was successful! Your account has been upgraded.")
        return render(request, 'payment_successful.html', {'customer': customer})

    except UserPayment.DoesNotExist:
        return redirect('register')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('premium_upgrade')

# View to handle cancelled payments
def payment_cancelled(request):
    messages.warning(request, "Payment was cancelled. Please try again.")
    return render(request, 'payment_cancelled.html')

# Stripe webhook to handle events from Stripe
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = config('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)
        time.sleep(15)

        try:
            user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
            user_payment.payment_bool = True
            user_payment.save()

            # send a confirmation email perhaps 
            try:
                user = request.user
                user_profile = Profile.objects.get(user=user)
                user_profile.premium = True
                user_profile.save()
            except Profile.DoesNotExist:
                return redirect('register')

        except UserPayment.DoesNotExist:
            return redirect('premium_upgrade')

    return HttpResponse(status=200)
