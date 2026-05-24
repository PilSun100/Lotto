from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from lottery.models import Round


class Command(BaseCommand):
    help = "Create a demo admin account and an open lottery round for browser testing."

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = "admin"
        password = "admin12345"

        admin_user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password(password)
        admin_user.save()

        now = timezone.now()
        round_, round_created = Round.objects.update_or_create(
            number=1,
            defaults={
                "sales_start": now - timezone.timedelta(days=1),
                "sales_end": now + timezone.timedelta(days=7),
                "is_drawn": False,
            },
        )

        account_status = "created" if created else "updated"
        round_status = "created" if round_created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Demo admin {account_status}: {username} / {password}"))
        self.stdout.write(self.style.SUCCESS(f"Demo round {round_status}: {round_}"))
