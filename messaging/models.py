from django.db import models
from users.models import User

class Session(models.Model):
    title = models.CharField(max_length=128, default='New Chat', verbose_name='title')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    timestamp = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class RecordMessage(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='records')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_records', null=True)
    image = models.ImageField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}"
