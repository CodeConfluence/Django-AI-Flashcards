from django.db import models
from flashcard_app.models import Flashcard_Set

class ChatHistory(models.Model):
    agent = models.ForeignKey(Flashcard_Set, on_delete=models.CASCADE, related_name='history')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    history = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name='messages')
    user_message = models.TextField(blank=True)
    bot_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
