from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Зв’язок із User")
    bio = models.TextField(blank=True, verbose_name="Текст «про себе»")

    def __str__(self):
        return f"Профіль {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True) 
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Отправитель")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Получатель")
    text = models.TextField(verbose_name="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Отправлено")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Личное сообщение"
        verbose_name_plural = "Личные сообщения"

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.text[:30]}"