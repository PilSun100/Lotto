from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .admin import run_draw
from .models import DrawResult, Round, Ticket
from .services import calculate_rank, generate_ticket_numbers, normalize_numbers


class LotteryServiceTests(TestCase):
    def test_generate_ticket_numbers_returns_six_unique_numbers_in_range(self):
        numbers = generate_ticket_numbers()

        self.assertEqual(len(numbers), 6)
        self.assertEqual(len(set(numbers)), 6)
        self.assertTrue(all(1 <= number <= 45 for number in numbers))

    def test_normalize_numbers_rejects_invalid_values(self):
        invalid_cases = [
            ["1", "2", "3"],
            ["1", "2", "3", "4", "5", "5"],
            ["1", "2", "3", "4", "5", "46"],
        ]

        for invalid_numbers in invalid_cases:
            with self.subTest(invalid_numbers=invalid_numbers):
                with self.assertRaises(ValueError):
                    normalize_numbers(invalid_numbers)

    def test_calculate_rank(self):
        winning_numbers = [1, 2, 3, 4, 5, 6]
        bonus_number = 7

        cases = [
            ([1, 2, 3, 4, 5, 6], "1등"),
            ([1, 2, 3, 4, 5, 7], "2등"),
            ([1, 2, 3, 4, 5, 8], "3등"),
            ([1, 2, 3, 4, 8, 9], "4등"),
            ([1, 2, 3, 8, 9, 10], "5등"),
            ([1, 2, 8, 9, 10, 11], "미당첨"),
        ]

        for ticket_numbers, expected_rank in cases:
            with self.subTest(expected_rank=expected_rank):
                self.assertEqual(calculate_rank(ticket_numbers, winning_numbers, bonus_number), expected_rank)


class TicketFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="buyer", password="password12345")
        self.other_user = user_model.objects.create_user(username="other", password="password12345")
        now = timezone.now()
        self.round = Round.objects.create(
            number=1,
            sales_start=now - timezone.timedelta(days=1),
            sales_end=now + timezone.timedelta(days=1),
        )

    def test_logged_in_user_can_buy_manual_ticket(self):
        self.client.login(username="buyer", password="password12345")

        response = self.client.post(
            reverse("ticket-buy"),
            {"purchase_type": Ticket.PurchaseType.MANUAL, "numbers": "1 2 3 4 5 6"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        ticket = Ticket.objects.get(user=self.user)
        self.assertEqual(ticket.numbers, [1, 2, 3, 4, 5, 6])

    def test_logged_in_user_can_buy_auto_ticket(self):
        self.client.login(username="buyer", password="password12345")

        response = self.client.post(
            reverse("ticket-buy"),
            {"purchase_type": Ticket.PurchaseType.AUTO},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        ticket = Ticket.objects.get(user=self.user)
        self.assertEqual(len(ticket.numbers), 6)

    def test_ticket_list_only_shows_current_user_tickets(self):
        Ticket.objects.create(
            user=self.user,
            round=self.round,
            numbers=[1, 2, 3, 4, 5, 6],
            purchase_type=Ticket.PurchaseType.MANUAL,
        )
        Ticket.objects.create(
            user=self.other_user,
            round=self.round,
            numbers=[7, 8, 9, 10, 11, 12],
            purchase_type=Ticket.PurchaseType.MANUAL,
        )
        self.client.login(username="buyer", password="password12345")

        response = self.client.get(reverse("ticket-list"))

        self.assertContains(response, "1, 2, 3, 4, 5, 6")
        self.assertNotContains(response, "7, 8, 9, 10, 11, 12")

    def test_ticket_result_changes_after_draw(self):
        ticket = Ticket.objects.create(
            user=self.user,
            round=self.round,
            numbers=[1, 2, 3, 4, 5, 6],
            purchase_type=Ticket.PurchaseType.MANUAL,
        )

        self.assertEqual(ticket.result_rank, "추첨 전")
        DrawResult.objects.create(round=self.round, winning_numbers=[1, 2, 3, 4, 5, 6], bonus_number=7)

        ticket.refresh_from_db()
        self.assertEqual(ticket.result_rank, "1등")

    def test_closed_round_rejects_new_ticket(self):
        self.round.sales_end = timezone.now() - timezone.timedelta(minutes=1)
        self.round.save()

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                user=self.user,
                round=self.round,
                numbers=[1, 2, 3, 4, 5, 6],
                purchase_type=Ticket.PurchaseType.MANUAL,
            )


class AdminDrawActionTests(TestCase):
    def test_admin_draw_action_creates_result(self):
        now = timezone.now()
        round_ = Round.objects.create(
            number=2,
            sales_start=now - timezone.timedelta(days=2),
            sales_end=now - timezone.timedelta(days=1),
        )

        class DummyAdmin:
            def message_user(self, request, message, level=None):
                pass

        run_draw(DummyAdmin(), None, Round.objects.filter(pk=round_.pk))

        round_.refresh_from_db()
        self.assertTrue(round_.is_drawn)
        self.assertTrue(DrawResult.objects.filter(round=round_).exists())
