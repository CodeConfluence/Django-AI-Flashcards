from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', blank=True)
    premium = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

class FlashcardSet(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcard_sets')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} by {self.creator.username}'

class Flashcard(models.Model):
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='flashcards')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Flashcard: {self.question[:50]}'

class FlashcardInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcard_interactions')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='interactions')
    user_answer = models.TextField()
    correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Interaction on {self.flashcard.question[:50]}'

class Resource(models.Model):
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='flashcard_resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Analytics(models.Model):
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='analytics')
    total_interactions = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    last_interaction = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Analytics for {self.flashcard_set.name}'

class Feedback(models.Model):
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback for {self.flashcard_set.name} by {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)