from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    m_sender = models.ForeignKey(User, on_delete=models.CASCADE,related_name="m_sender")
    m_receiver = models.ForeignKey(User, on_delete=models.CASCADE,related_name="m_receiver")
    sent_at = models.DateTimeField(default=timezone.now)
    text = models.CharField(max_length=5000)

    def __str__(self):
        return f"{self.m_sender} -> {self.m_receiver}"
    
    @classmethod
    def get_all_conversations(cls, user):
        messages = cls.objects.filter(models.Q(m_sender=user) | models.Q(m_receiver=user))
        users_in_conversations = User.objects.filter(
            id__in=messages.values_list('m_sender', flat=True).union(messages.values_list('m_receiver', flat=True))
        ).distinct()
        users_in_conversations = users_in_conversations.exclude(id=user.id)

        return users_in_conversations
    
    @classmethod
    def get_all_messages(cls, user, other_user):
        messages = cls.objects.filter(
            (models.Q(m_sender=user) & models.Q(m_receiver=other_user)) |
            (models.Q(m_sender=other_user) & models.Q(m_receiver=user))
        ).order_by('-sent_at')

        return messages