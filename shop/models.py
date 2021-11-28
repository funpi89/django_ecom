from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe
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

    def image_preview(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.primary_image.url)) if self.primary_image else '-'
    image_preview.short_description = '圖片預覽'

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
    name = models.CharField('姓名', max_length=15, blank=True, null=True)
    phone = models.CharField('電話', max_length=15, blank=True, null=True)
    address = models.CharField('地址', max_length=127, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
      return f"{self.id}"

    class Meta:
        verbose_name = '訂單'
        verbose_name_plural = '訂單'

class Mapping(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='訂單')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='產品')
    quantity = models.IntegerField('總價', default=1)
    # subtotal = models.DecimalField('小計', max_digits=6, decimal_places=2, default=0.00)
    @property
    def subtotal(self):
        return self.product.discounted_price * self.quantity

    def __str__(self):
        return f"訂單編號: {self.order.id}-{self.product.title}"

    class Meta:
        verbose_name = '訂單產品'
        verbose_name_plural = '訂單產品'

    # def save(self, *args, **kwargs):
    #     super(Mapping, self).save(*args, **kwargs)
    #     self.update_order_total()
    #
    # def delete(self, *args, **kwargs):
    #     order = self.order
    #     super(Mapping, self).delete(*args, **kwargs)
    #     output = Mapping.objects.filter(order=order).aggregate(t=Sum(F('product__discounted_price') * F('quantity')))
    #     order.total = output['t'] if output['t'] is not None else 0.0
    #     order.save()

    # def update_order_total(self):
    #     '''
    #     self.order.total 更新總價
    #     '''
    #     order = self.order
    #     output = Mapping.objects.filter(order=order).aggregate(t=Sum(F('product__discounted_price') * F('quantity')))
    #     order.total = output['t']
    #     order.save()

# def update_order_total(order):
#     output = Mapping.objects.filter(order=order).aggregate(t=Sum(F('product__discounted_price') * F('quantity')))
#     order.total = output['t'] if output['t'] is not None else 0.0
#     order.save()
#
# @receiver(post_save, sender=Mapping)
# def mapping_post_save(sender, *args, **kwargs):
#     instance = kwargs['instance']
#     order = instance.order
#     update_order_total(order)
#
# @receiver(post_delete, sender=Mapping)
# def mapping_post_delete(sender, *args, **kwargs):
#     instance = kwargs['instance']
#     order = instance.order
#     update_order_total(order)

@receiver(post_delete, sender=Mapping)
@receiver(post_save, sender=Mapping)
def update_order_total(sender, *args, **kwargs):
    instance = kwargs['instance']
    order = instance.order
    output = Mapping.objects.filter(order=order).aggregate(t=Sum(F('product__discounted_price') * F('quantity')))
    order.total = output['t'] if output['t'] is not None else 0.0
    order.save()
