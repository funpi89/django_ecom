from django.contrib import admin

from shop.models import Product, Category, Order, Mapping
# Register your models here.

admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(Order)
admin.site.register(Mapping)

class ShopAdminSite(admin.AdminSite):
    site_header = '商品後台'
    index_title = '商品後台'

shop_admin = ShopAdminSite(name='ShopAdmin')
shop_admin.register(Category)
shop_admin.register(Product)
shop_admin.register(Order)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'category', 'original_price', 'discounted_price']
    search_fields = ['title', 'description']
    list_filter = ['category']
    list_display_links = ['title']
    readonly_fields = ['image_preview']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'created_at', 'updated_at', 'total']
    list_editable = ['status']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'phone', 'address']