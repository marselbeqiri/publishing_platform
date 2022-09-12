from django.contrib.auth.models import AbstractUser
from django.db import models

from applications.authentication.constants import GROUPS
from applications.authentication.models import Interest
from applications.authentication.models.user_manager import UserManager


class User(AbstractUser):
    email = models.EmailField(blank=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]
    objects = UserManager()
    short_biography = models.CharField(max_length=1000, blank=True)
    birth_date = models.DateField(null=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    interests = models.ManyToManyField(to=Interest, verbose_name="List of Interests")

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.get_full_name()

    def is_admin(self) -> bool:
        return self.groups.filter(name=GROUPS.ADMIN).exists()

    def is_blogger(self) -> bool:
        return self.groups.filter(name=GROUPS.BLOGGER).exists()

    @property
    def total_posts(self):
        return self.posts.count()
