from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name="Elektron pochta",
        error_messages={
            'unique': "Bu email manzili bilan allaqachon hisob ochilgan.",
        }
    )

    def __str__(self):
        return self.username
