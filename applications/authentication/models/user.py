from django.contrib.auth.models import AbstractUser
from django.db import models

from applications.authentication.constants import GROUPS
from applications.authentication.models.user_manager import UserManager


class User(AbstractUser):
    email = models.EmailField(blank=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]
    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.get_full_name()

    def is_admin(self) -> bool:
        return self.groups.filter(name=GROUPS.ADMIN).exists()

    def is_blogger(self) -> bool:
        return self.groups.filter(name=GROUPS.BLOGGER).exists()
