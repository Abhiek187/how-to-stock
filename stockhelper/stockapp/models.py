from django.db import models
import uuid


class Stock(models.Model):
    pass

# Object representing the flashcards
class Card(models.Model):
    # UUIDs are more secure than the default id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=50)
    definition = models.TextField()

    def __str__(self):
        return f"{self.word} - {self.definition}"
