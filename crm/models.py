from django.db import models
from django.conf import settings
# Create your models here.

User = settings.AUTH_USER_MODEL

class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name='使用者', on_delete=models.CASCADE)
    phone = models.CharField('電話', max_length=15, blank=True, null=True)
    address = models.CharField('地址', max_length=127, blank=True, null=True)
