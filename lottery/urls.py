from django.urls import path

from .views import TicketListView, TicketPurchaseView


urlpatterns = [
    path("", TicketListView.as_view(), name="ticket-list"),
    path("buy/", TicketPurchaseView.as_view(), name="ticket-buy"),
]
