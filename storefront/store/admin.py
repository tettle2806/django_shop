from django.contrib import admin
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}"  class="thumbnail">')
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    list_display = ['title', 'unit_price', 'inventory_status',
                    'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    inlines = [ProductImageInline]
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']


    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    class Media:
        css = {
            'all': ['store/style.css']
        }


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
            'collection__id': str(collection.id)
        })
        )
        return format_html(f'<a href="{url}">{collection.products_count} Products</a>')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

# @admin.register(models.Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ['first_name', 'last_name', 'membership', 'orders']
#     list_editable = ['membership']
#     list_per_page = 10
#     ordering = ['first_name', 'last_name']
#     search_fields = ['first_name__istartswith', 'last_name__istartswith']
#
#     @admin.display(ordering='orders_count')
#     def orders(self, customer):
#         url = (
#             reverse('admin:store_order_changelist')
#             + '?'
#             + urlencode({
#             'customer__id': str(customer.id)
#         })
#         )
#         return format_html(f'<a href="{url}">{customer.orders_count} Orders</a>')
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).annotate(
#             orders_count=Count('order')
#         )


class OrderItemInline(admin.TabularInline):
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']