from django.http import JsonResponse
from django.db import IntegrityError

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from django.contrib.auth.password_validation import validate_password

from backend.filters import ProductInfoFilter

from backend.serializers import UserSerializer, ContactSerializer
from backend.serializers import OrderItemSerializer, OrderSerializer
from backend.serializers import ShopSerializer, ProductInfoSerializer, CategorySerializer

from backend import tasks

from yaml import load as load_yaml, Loader
from ujson import loads as load_json

from django.db.models import Q, F, Sum
from distutils.util import strtobool

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.permissions import IsShopUser

from backend.models import Contact, ConfirmEmailToken
from backend.models import Parameter, ProductParameter
from backend.models import Product, ProductInfo
from backend.models import Order, OrderItem
from backend.models import Shop, Category


import requests


class RegisterAccount(APIView):
    """Регистрация пользователя"""

    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password'}.issubset(request.data):
            try:
                # Проверка пароля на сложность
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # Проверка на уникальность имени пользователя
                request.data._mutable = True
                request.data.update({})

                user_serializer = UserSerializer(data=request.data)

                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()

                    tasks.new_user_registered_task.delay(user.id)

                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """Класс для подтверждения почтового адреса"""

    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']
            ).first()

            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()

                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):
    """Класс для просмотра и редактирования данных пользователя"""

    permission_classes = [IsAuthenticated]

    # Получить мою информацию
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # Редактирование моей информации
    def post(self, request, *args, **kwargs):
        # Если в request.data есть пароль
        if 'password' in request.data:
            # Проверка пароля на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data['password'])

        # Проверка остальных данных
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class ContactView(APIView):
    """Класс для работы с контактами покупателей"""

    permission_classes = [IsAuthenticated]

    # Получить мои контакты
    def get(self, request, *args, **kwargs):
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    # Добавить новый контакт
    def post(self, request, *args, **kwargs):
        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # Редактировать контакт
    def put(self, request, *args, **kwargs):
        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()

                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)

                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # Удалить контакт
    def delete(self, request, *args, **kwargs):
        items_sting = request.data.get('items')

        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False

            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class SellerUpdateCatalog(APIView):
    """Класс для обновления каталога от продавца"""

    permission_classes = [IsAuthenticated, IsShopUser]

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')

        if url:
            validate_url = URLValidator()

            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = requests.get(url).content
                data = load_yaml(stream, Loader=Loader)

                # Если у пользователя нет магазина - создать
                if not Shop.objects.filter(user_id=request.user.id).exists():
                    shop = Shop.objects.create(name=data['shop'], user_id=request.user.id)
                # Иначе получить магазин
                else:
                    shop = Shop.objects.get(user_id=request.user.id)

                # И обновить название
                shop.name = data['shop']
                shop.save()

                for category in data['categories']:
                    if not Category.objects.filter(id=category['id']).exists():
                        category_object = Category.objects.create(id=category['id'], name=category['name'])
                    else:
                        category_object = Category.objects.get(id=category['id'])

                    category_object.shops.add(shop.id)
                    category_object.save()

                ProductInfo.objects.filter(shop_id=shop.id).delete()

                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)

                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class SellerState(APIView):
    """Класс для работы со статусом продавца"""

    permission_classes = [IsAuthenticated, IsShopUser]

    # Получить текущий статус
    def get(self, request, *args, **kwargs):
        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # Изменить текущий статус
    def post(self, request, *args, **kwargs):
        state = request.data.get('state')

        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ProductInfoView(ListAPIView):
    """Класс для поиска товаров"""

    queryset = ProductInfo.objects.filter(shop__state=True).select_related(
        'shop', 'product__category'
    ).prefetch_related('product_parameters__parameter').distinct()

    serializer_class = ProductInfoSerializer
    filterset_class = ProductInfoFilter


class ProductInfoRetrieve(RetrieveAPIView):
    """Класс для получения конкретного товара"""

    queryset = ProductInfo.objects.filter(shop__state=True).select_related(
        'shop', 'product__category'
    ).prefetch_related('product_parameters__parameter').distinct()

    serializer_class = ProductInfoSerializer


class CategoryView(ListAPIView):
    """Класс для просмотра категорий"""

    queryset = Category.objects.filter(shops__state=True)
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """Класс для просмотра списка магазинов"""

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class CartView(APIView):
    """Класс для работы с корзиной покупателя"""

    permission_classes = [IsAuthenticated]

    # Получить корзину
    def get(self, request, *args, **kwargs):
        cart = Order.objects.filter(
            user_id=request.user.id, status='cart').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(cart, many=True)
        return Response(serializer.data)

    # Добавить товары в корзину
    def post(self, request, *args, **kwargs):
        items_sting = request.data.get('items')

        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                cart, _ = Order.objects.get_or_create(user_id=request.user.id, status='cart')
                objects_created = 0

                for order_item in items_dict:
                    order_item.update({'order': cart.id})
                    serializer = OrderItemSerializer(data=order_item)

                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

                return JsonResponse({'Status': True, 'Создано объектов': objects_created})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # Редактировать количество товаров в корзине
    def patch(self, request, *args, **kwargs):
        items_sting = request.data.get('items')

        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                cart, _ = Order.objects.get_or_create(user_id=request.user.id, status='cart')
                objects_updated = 0

                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=cart.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # Удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        items_sting = request.data.get('items')

        if items_sting:
            items_list = items_sting.split(',')

            cart, _ = Order.objects.get_or_create(user_id=request.user.id, status='cart')

            query = Q()
            objects_deleted = False

            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=cart.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):
    """Класс для получения заказов и оформления их из корзины"""

    permission_classes = [IsAuthenticated]

    # Получить список моих заказов
    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(
            user_id=request.user.id).exclude(status='cart').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # Оформить заказ из корзины
    def post(self, request, *args, **kwargs):
        if {'cart_id', 'contact'}.issubset(request.data):
            if request.data['cart_id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['cart_id']).update(
                        contact_id=request.data['contact'],
                        status='new')
                except IntegrityError as error:
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        tasks.new_user_registered_task.delay(ser_id=request.user.id, status='new')
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class SellerOrderView(APIView):
    """Класс для получения заказов продавцами"""

    permission_classes = [IsAuthenticated, IsShopUser]

    # Получить заказы
    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(status='cart').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # Изменить статус заказа
    def patch(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        status = request.data.get('status')

        if status not in [status[0] for status in Order.ORDER_STATUS]:
            return JsonResponse({'Status': False, 'Errors': 'Указан неверный статус заказа'})

        if order_id and status:
            try:
                is_updated = Order.objects.filter(
                    ordered_items__product_info__shop__user_id=request.user.id, id=order_id
                ).exclude(status__in=['cart', 'delivered']).update(status=status)
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})
            else:
                if is_updated:
                    tasks.new_user_registered_task.delay(ser_id=request.user.id, status=status)
                    return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
