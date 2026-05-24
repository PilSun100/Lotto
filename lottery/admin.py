from django.contrib import admin, messages

from .models import DrawResult, Round, Ticket
from .services import generate_draw_numbers


@admin.action(description="선택한 회차 추첨 실행")
def run_draw(modeladmin, request, queryset):
    created_count = 0
    for round_ in queryset:
        if round_.is_drawn or hasattr(round_, "draw_result"):
            modeladmin.message_user(
                request,
                f"{round_}는 이미 추첨이 완료되었습니다.",
                level=messages.WARNING,
            )
            continue

        winning_numbers, bonus_number = generate_draw_numbers()
        DrawResult.objects.create(
            round=round_,
            winning_numbers=winning_numbers,
            bonus_number=bonus_number,
        )
        round_.is_drawn = True
        round_.save(update_fields=["is_drawn"])
        created_count += 1

    modeladmin.message_user(request, f"{created_count}개 회차의 추첨을 완료했습니다.")


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("number", "sales_start", "sales_end", "is_drawn", "ticket_count")
    list_filter = ("is_drawn",)
    search_fields = ("number",)
    actions = [run_draw]

    @admin.display(description="판매 수")
    def ticket_count(self, obj):
        return obj.tickets.count()


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "round",
        "purchase_type",
        "display_numbers",
        "result_rank",
        "purchased_at",
    )
    list_filter = ("round", "purchase_type", "purchased_at")
    search_fields = ("user__username", "round__number")
    readonly_fields = ("purchased_at", "result_rank")


@admin.register(DrawResult)
class DrawResultAdmin(admin.ModelAdmin):
    list_display = ("round", "display_winning_numbers", "bonus_number", "drawn_at")
    list_filter = ("drawn_at",)
    readonly_fields = ("round", "winning_numbers", "bonus_number", "drawn_at")

    def has_add_permission(self, request):
        return False
