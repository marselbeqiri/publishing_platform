from django.db import models


class GROUPS(models.TextChoices):
    ADMIN: str = "Admin"
    BLOGGER: str = "Blogger"
