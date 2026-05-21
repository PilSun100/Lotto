from django import forms

from .models import Ticket
from .services import generate_ticket_numbers, normalize_numbers


class TicketPurchaseForm(forms.Form):
    purchase_type = forms.ChoiceField(
        choices=Ticket.PurchaseType.choices,
        widget=forms.RadioSelect,
        initial=Ticket.PurchaseType.AUTO,
        label="구매 방식",
    )
    numbers = forms.CharField(
        required=False,
        label="수동 번호",
        help_text="수동 구매 시 1~45 사이 숫자 6개를 쉼표 또는 공백으로 입력하세요.",
    )

    def clean(self):
        cleaned_data = super().clean()
        purchase_type = cleaned_data.get("purchase_type")
        raw_numbers = cleaned_data.get("numbers", "")

        if purchase_type == Ticket.PurchaseType.AUTO:
            cleaned_data["numbers"] = generate_ticket_numbers()
            return cleaned_data

        parts = raw_numbers.replace(",", " ").split()
        try:
            cleaned_data["numbers"] = normalize_numbers(parts)
        except ValueError as exc:
            raise forms.ValidationError(str(exc))

        return cleaned_data
