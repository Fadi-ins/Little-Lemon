from django.core.management.base import BaseCommand
from restaurant.models import Menu

class Command(BaseCommand):
    help = "Add sample menu items without replacing existing items."

    def handle(self, *args, **options):
        for title, price, inventory in [
            ("Greek Salad", "12.50", 30), ("Bruschetta", "7.00", 40),
            ("Grilled Fish", "22.00", 15), ("Lemon Dessert", "6.50", 25),
        ]:
            Menu.objects.get_or_create(title=title, defaults={"price": price, "inventory": inventory})
        self.stdout.write(self.style.SUCCESS("Sample menu is ready."))
