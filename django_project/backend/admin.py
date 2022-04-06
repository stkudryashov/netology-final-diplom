from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import User, Contact, ConfirmEmailToken
from backend.models import Parameter, ProductParameter
from backend.models import Product, ProductInfo
from backend.models import Order, OrderItem
from backend.models import Shop, Category


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Панель управления пользователями"""

    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('shop', 'model', 'external_id', 'quantity', 'price', 'price_rrc')
    search_fields = ('model', 'external_id')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
