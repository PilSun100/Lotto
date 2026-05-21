from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .services import calculate_rank, normalize_numbers


class Round(models.Model):
    number = models.PositiveIntegerField(unique=True, verbose_name="회차")
    sales_start = models.DateTimeField(verbose_name="판매 시작")
    sales_end = models.DateTimeField(verbose_name="판매 종료")
    is_drawn = models.BooleanField(default=False, verbose_name="추첨 완료")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-number"]
        verbose_name = "회차"
        verbose_name_plural = "회차"

    def __str__(self):
        return f"{self.number}회차"

    @property
    def is_open(self):
        now = timezone.now()
        return self.sales_start <= now <= self.sales_end and not self.is_drawn

    def clean(self):
        if self.sales_start >= self.sales_end:
            raise ValidationError("판매 종료 시각은 판매 시작 시각보다 늦어야 합니다.")


class Ticket(models.Model):
    class PurchaseType(models.TextChoices):
        MANUAL = "manual", "수동"
        AUTO = "auto", "자동"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="tickets")
    numbers = models.JSONField(verbose_name="선택 번호")
    purchase_type = models.CharField(max_length=10, choices=PurchaseType.choices)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]
        verbose_name = "복권"
        verbose_name_plural = "복권"

    def __str__(self):
        return f"{self.user} - {self.round} - {self.display_numbers}"

    @property
    def display_numbers(self):
        return ", ".join(str(number) for number in self.numbers)

    @property
    def result_rank(self):
        if not hasattr(self.round, "draw_result"):
            return "추첨 전"
        result = self.round.draw_result
        return calculate_rank(self.numbers, result.winning_numbers, result.bonus_number)

    def clean(self):
        self.numbers = normalize_numbers(self.numbers)
        if self.round_id and not self.round.is_open and not self.pk:
            raise ValidationError("판매 중인 회차에만 복권을 구매할 수 있습니다.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class DrawResult(models.Model):
    round = models.OneToOneField(Round, on_delete=models.CASCADE, related_name="draw_result")
    winning_numbers = models.JSONField(verbose_name="당첨 번호")
    bonus_number = models.PositiveIntegerField(verbose_name="보너스 번호")
    drawn_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-drawn_at"]
        verbose_name = "추첨 결과"
        verbose_name_plural = "추첨 결과"

    def __str__(self):
        return f"{self.round} 당첨 결과"

    @property
    def display_winning_numbers(self):
        return ", ".join(str(number) for number in self.winning_numbers)

    def clean(self):
        self.winning_numbers = normalize_numbers(self.winning_numbers)
        if self.bonus_number in self.winning_numbers:
            raise ValidationError("보너스 번호는 당첨 번호와 중복될 수 없습니다.")
        if self.bonus_number < 1 or self.bonus_number > 45:
            raise ValidationError("보너스 번호는 1부터 45 사이여야 합니다.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
