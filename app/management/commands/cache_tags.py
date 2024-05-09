from django.core.management import BaseCommand
from app.views import cache_users

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache_users()