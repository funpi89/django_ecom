from django.db import models
from django.conf import settings
# Create your models here.

User = settings.AUTH_USER_MODEL

class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name='使用者', on_delete=models.CASCADE)
    phone = models.CharField('電話', max_length=15, blank=True, null=True)
    address = models.CharField('地址', max_length=127, blank=True, null=True)

    class Meta:
        verbose_name = '使用者檔案'
        verbose_name_plural = '使用者檔案'


class ContactForm(models.Model):
    user = models.ForeignKey(User, verbose_name='使用者', on_delete=models.CASCADE)
    phone = models.CharField('電話', max_length=15, blank=True, null=True)
    email = models.EmailField()
    created_at = models.DateTimeField('建立日期', auto_now_add=True)
    contacted = models.BooleanField('已聯絡', default=False)

    class Meta:
        verbose_name = '聯絡表單'
        verbose_name_plural = '聯絡表單'

