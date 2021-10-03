from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


# The user (extends Django's existing User object)
class User(AbstractUser):
    # Start off with a default balance of $10,000
    balance = models.DecimalField(
        max_digits=7, decimal_places=2, default=10000)


# Information about each stock
class Stock(models.Model):
    # Each stock ticker is unique
    ticker = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100, default="")
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    change = models.FloatField(default=0)

    def __str__(self):
        return f"{self.ticker} - {self.name}"


# The user's stock portfolio
class Portfolio(models.Model):
    # UUIDs are more secure than the default id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # One user can own many stocks
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    # Many portfolios from different users can contain the same stock
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user}: {self.shares} {'share' if self.shares == 1 else 'shares'} of {self.stock}"


# Object representing the flashcards
class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=50)
    definition = models.TextField()

    def __str__(self):
        return f"{self.word} - {self.definition}"
