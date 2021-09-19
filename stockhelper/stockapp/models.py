from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


# The user (extends Django's existing User object)
class User(AbstractUser):
    # Start off with a default balance of $10,000
    balance = models.DecimalField(
        max_digits=7, decimal_places=2, default=10000)


# The user's stock portfolio
class Stock(models.Model):
    # One user can own many stocks
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10, primary_key=True, default="")
    name = models.CharField(max_length=100, default="")
    shares = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    change = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user}: {self.ticker} - {self.name}"


# Object representing the flashcards
class Card(models.Model):
    # UUIDs are more secure than the default id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=50)
    definition = models.TextField()

    def __str__(self):
        return f"{self.word} - {self.definition}"
