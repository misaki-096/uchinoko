from django.db import models
from accounts.models import User


class Keyword(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "keywords"
