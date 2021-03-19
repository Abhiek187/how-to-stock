from django.db import models
import uuid


# Placeholder model for generic views
class Dummy(models.Model):
    pass


# The user's stock portfolio
class Stock(models.Model):
    ticker = models.CharField(max_length=10, primary_key=True, default="")
    name = models.CharField(max_length=100, default="")
    shares = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    change = models.FloatField(default=0)

    def __str__(self):
        return f"{self.ticker} - {self.name}"


# Object representing the flashcards
class Card(models.Model):
    # UUIDs are more secure than the default id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=50)
    definition = models.TextField()

    def __str__(self):
        return f"{self.word} - {self.definition}"
