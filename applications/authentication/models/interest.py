from django.db import models


class Interest(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "User Interest"
        verbose_name_plural = "User Interests"
        ordering = ["name"]
