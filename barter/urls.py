from django.urls import path
from . import views

urlpatterns = [
    path('offer/send/<int:product_id>/', views.send_offer, name='send_offer'),
    path('offers/received/', views.received_offers, name='received_offers'),
    path('offers/sent/', views.sent_offers, name='sent_offers'),
    path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail'),
    path('offer/<int:offer_id>/accept/', views.accept_offer, name='accept_offer'),
    path('offer/<int:offer_id>/reject/', views.reject_offer, name='reject_offer'),
    path('match/<int:product_id>/', views.match_products, name='match_products'),
    path('chat/<int:offer_id>/', views.offer_chat_page, name='offer_chat_page'),
    path('api/messages/<int:offer_id>/', views.api_get_messages, name='api_get_messages'),
    path('api/messages/<int:offer_id>/send/', views.api_send_message, name='api_send_message'),
    path('send-offer/<int:product_id>/', views.send_offer, name='send_offer'),
    path("offer-notify/", views.offer_notification_count, name="offer_notification_count"),


]
