import django_filters as filters

from backend.models import ProductInfo


class ProductInfoFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    shop_id = filters.NumberFilter(field_name='shop_id', lookup_expr='exact')
    category_id = filters.NumberFilter(field_name='product__category_id', lookup_expr='exact')

    class Meta:
        model = ProductInfo
        fields = ['name', 'shop_id', 'category_id']
