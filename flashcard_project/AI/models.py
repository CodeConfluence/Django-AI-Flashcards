from django.db import models
from flashcard_app.models import Flashcard_Set
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'model_default_instructions.txt')

try:
    with open(file_path, 'r') as file:
        default_instructions = file.read()
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    default_instructions = ""

def upload_resource_path(instance, filename):
    return f'uploads/flashcard_sets/{instance.Flashcard_Set.id}/{filename}'

class Resource(models.Model):
    flashcard_set = models.ForeignKey(Flashcard_Set, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_resource_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
