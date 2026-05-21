from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView

from .forms import TicketPurchaseForm
from .models import Round, Ticket


class HomeView(TemplateView):
    template_name = "lottery/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_round"] = next((round_ for round_ in Round.objects.all() if round_.is_open), None)
        return context


class TicketPurchaseView(LoginRequiredMixin, FormView):
    template_name = "lottery/ticket_form.html"
    form_class = TicketPurchaseForm
    success_url = reverse_lazy("ticket-list")

    def dispatch(self, request, *args, **kwargs):
        self.current_round = next((round_ for round_ in Round.objects.all() if round_.is_open), None)
        if self.current_round is None:
            messages.error(request, "현재 판매 중인 회차가 없습니다.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        Ticket.objects.create(
            user=self.request.user,
            round=self.current_round,
            numbers=form.cleaned_data["numbers"],
            purchase_type=form.cleaned_data["purchase_type"],
        )
        messages.success(self.request, "복권 구매가 완료되었습니다.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_round"] = self.current_round
        return context


class TicketListView(LoginRequiredMixin, ListView):
    template_name = "lottery/ticket_list.html"
    context_object_name = "tickets"

    def get_queryset(self):
        return (
            Ticket.objects.filter(user=self.request.user)
            .select_related("round")
            .order_by("-purchased_at")
        )
