from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, F
# Create your models here.

User = settings.AUTH_USER_MODEL

def path_and_rename(instance, filename):
    ext = filename.split('.')[-1]
    now = timezone.now()
    return f"{now.year}{now.month}{now.day}/{uuid4().hex}.{ext}"


class Category(models.Model):
    title = models.CharField('標題', max_length=63)
    primary_image = models.ImageField('圖片', null=True, default=None, upload_to=path_and_rename)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '產品類別'
        verbose_name_plural = '產品類別'

class Product(models.Model):
    title = models.CharField('標題', max_length=127)
    description = models.TextField('描述', blank=True, null=True)
    primary_image = models.ImageField('主要圖片', null=True, default=None, upload_to=path_and_rename)
    original_price = models.DecimalField('原價', max_digits=6, decimal_places=2, default=0.00)
    discounted_price = models.DecimalField('特價', max_digits=6, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='產品類別')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '產品'
        verbose_name_plural = '產品'

class Order(models.Model):

    class StatusChoice(models.TextChoices):
        ORDER_SENT = 'order_sent', '已下單'
        PAID = 'paid', '已付款'
        INVOICE_MADE = 'invoice_made', '已開立發票'
        PRODUCT_SENT = 'product_sent', '已寄出'
        ORDER_CLOSED = 'order_closed', '訂單結束'
        ORDER_FAILED = 'order_failed', '訂單失敗'

    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="客戶")
    created_at = models.DateTimeField('建立於', auto_now_add=True)
    updated_at = models.DateTimeField('更新於', auto_now=True)
    total = models.DecimalField('總計', max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField('訂單狀態', max_length=63, choices=StatusChoice.choices, default=StatusChoice.ORDER_SENT)
    products = models.ManyToManyField(Product, verbose_name='訂單內容', related_name='orders', through='Mapping')

    def __str__(self):
      return f"{self.id}"

    class Meta:
        verbose_name = '訂單'
        verbose_name_plural = '訂單'

class Mapping(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='訂單')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='產品')
    quality = models.IntegerField(default=1)
    # subtotal = models.DecimalField('小計', max_digits=6, decimal_places=2, default=0.00)
    @property
    def subtotal(self):
        return self.product.discounted_price * self.quality

    def __str__(self):
        return f"訂單編號: {self.order.id}-{self.product.title}"

    class Meta:
        verbose_name = '訂單產品'
        verbose_name_plural = '訂單產品'

    def save(self, *args, **kwargs):
        super(Mapping, self).save(*args, **kwargs)
        self.update_order_total()

    def delete(self, *args, **kwargs):
        order = self.order
        super(Mapping, self).delete(*args, **kwargs)
        output = Mapping.objects.filter(order=order).aggregate(t=Sum(F('product__discounted_price') * F('quality')))
        order.total = output['t'] if output['t'] is not None else 0.0
        order.save()

    def update_order_total(self):
        '''
        self.order.total 更新總價
        '''
        order = self.order
        output = Mapping.objects.filter(order=order).aggregate(t=Sum(F('product__discounted_price') * F('quality')))
        order.total = output['t']
        order.save()
