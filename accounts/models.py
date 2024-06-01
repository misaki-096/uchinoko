from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager,
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=254)
    email = models.EmailField(unique=True, verbose_name="メールアドレス")
    is_staff = models.BooleanField(default=False)
    groups = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
