from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Offer, Chat
from products.models import Product
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone

# Send Offer
from django.contrib import messages

@login_required
def send_offer(request, product_id):
    receiver_product = get_object_or_404(Product, id=product_id)
    sender_products = Product.objects.filter(user=request.user)

    if request.method == 'POST':
        sender_product_id = request.POST['sender_product']
        sender_product = Product.objects.get(id=sender_product_id)

        Offer.objects.create(
            sender=request.user,
            receiver=receiver_product.user,
            sender_product=sender_product,
            receiver_product=receiver_product
        )

        messages.success(request, f'Offer sent! Go to Sent Offers to see it. You can chat once accepted.')
        return redirect('sent_offers')

    return render(request, 'barter/send_offer.html', {
        'receiver_product': receiver_product,
        'sender_products': sender_products
    })



# View Offers
@login_required
def received_offers(request):
    offers = Offer.objects.filter(receiver=request.user)
    return render(request, 'barter/received_offers.html', {'offers': offers})


@login_required
def sent_offers(request):
    offers = Offer.objects.filter(sender=request.user)
    return render(request, 'barter/sent_offers.html', {'offers': offers})


# Offer Details
@login_required
def offer_detail(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    return render(request, 'barter/offer_detail.html', {'offer': offer})


# Accept / Reject
@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.status = 'accepted'
    offer.save()
    return redirect('received_offers')


@login_required
def reject_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.status = 'rejected'
    offer.save()
    return redirect('received_offers')


# AI Matching — Simple Version
@login_required
def match_products(request, product_id):
    my_product = get_object_or_404(Product, id=product_id)

    matches = Product.objects.exclude(user=request.user).filter(
        category=my_product.category
    )

    return render(request, 'barter/match_products.html', {
        'my_product': my_product,
        'matches': matches
    })


@login_required
def offer_chat_page(request, offer_id):
    # renders the chat page (HTML) where JS will poll for messages
    offer = get_object_or_404(Offer, id=offer_id)
    # ensure only participants can open this page
    if request.user != offer.sender and request.user != offer.receiver:
        return HttpResponseBadRequest("Not allowed")
    return render(request, 'barter/chat.html', {'offer': offer})

@login_required
def api_get_messages(request, offer_id):
    # returns JSON list of messages for the offer
    offer = get_object_or_404(Offer, id=offer_id)
    # permission
    if request.user != offer.sender and request.user != offer.receiver:
        return JsonResponse({'error': 'forbidden'}, status=403)

    # optional: allow "since" param to fetch only newer messages (timestamp in ISO)
    since = request.GET.get('since')
    qs = Chat.objects.filter(offer=offer)
    if since:
        try:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(since)
            if dt:
                qs = qs.filter(timestamp__gt=dt)
        except Exception:
            pass

    messages = [
        {
            'id': c.id,
            'sender_id': c.sender.id,
            'sender_username': c.sender.username,
            'message': c.message,
            'timestamp': c.timestamp.isoformat()
        } for c in qs.order_by('timestamp')
    ]
    return JsonResponse({'messages': messages})

# barter/views.py


@login_required
@require_POST
def api_send_message(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    # Only sender or receiver can send messages
    if request.user != offer.sender and request.user != offer.receiver:
        return JsonResponse({'error': 'forbidden'}, status=403)

    message_text = request.POST.get('message')
    if not message_text:
        return JsonResponse({'error': 'empty message'}, status=400)

    chat = Chat.objects.create(
        offer=offer,
        sender=request.user,
        message=message_text
    )

    return JsonResponse({
        'message': {
            'id': chat.id,
            'sender_id': chat.sender.id,
            'sender_username': chat.sender.username,
            'message': chat.message,
            'timestamp': chat.timestamp.isoformat()
        }
    })


@login_required
def match_products(request, product_id):
    my_product = Product.objects.get(id=product_id)

    # Simple match by category + estimated_value range
    matches = Product.objects.exclude(user=request.user).filter(
        category=my_product.category,
        estimated_value__gte=my_product.estimated_value*0.8,
        estimated_value__lte=my_product.estimated_value*1.2
    )

    return render(request, 'barter/match_products.html', {
        'my_product': my_product,
        'matches': matches
    })

# barter/views.py
@login_required
def add_review(request, offer_id):
    offer = Offer.objects.get(id=offer_id)
    if request.user != offer.sender and request.user != offer.receiver:
        return HttpResponseBadRequest("Not allowed")

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = offer.receiver if request.user == offer.sender else offer.sender
            review.offer = offer
            review.save()
            return redirect('offer_detail', offer_id=offer.id)
    else:
        form = ReviewForm()
    return render(request, 'barter/add_review.html', {'form': form, 'offer': offer})

@login_required
def offer_notification_count(request):
    count = Offer.objects.filter(receiver=request.user, status='pending').count()
    return JsonResponse({'count': count})
