from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from applications.common.constants import GROUPS


class Command(BaseCommand):
    help = 'Create Init Data'
    default_password = 'Demo@123!'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        admin_group, blogger_group = self.create_groups()
        user_model = get_user_model()

        if not user_model.objects.filter(username='admin').exists():
            admin = user_model.objects.create_superuser(
                username='admin',
                password=self.default_password,
                first_name='Admin',
                last_name='Admin',
                is_superuser=True,
            )
            admin.groups.add(admin_group.id)
            admin.groups.add(blogger_group.id)
            admin.save()

        if not user_model.objects.filter(username='blogger').exists():
            blogger = user_model.objects.create_user(
                username='blogger',
                password=self.default_password,
                first_name='Ross',
                last_name='Geller'
            )
            blogger.groups.add(blogger_group.id)
            blogger.save()

    def create_groups(self):
        admin = Group.objects.get_or_create(name=GROUPS.ADMIN)[0]
        blogger = Group.objects.get_or_create(name=GROUPS.BLOGGER)[0]

        return admin, blogger
