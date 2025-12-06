from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Offer(models.Model):
    sender = models.ForeignKey(User, related_name='sent_offers', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_offers', on_delete=models.CASCADE)
    sender_product = models.ForeignKey(Product, related_name='sender_product', on_delete=models.CASCADE)
    receiver_product = models.ForeignKey(Product, related_name='receiver_product', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')  # pending/accepted/rejected
    created_at = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
