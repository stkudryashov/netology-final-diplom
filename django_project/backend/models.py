from django.db import models

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.validators import UnicodeUsernameValidator

from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator


class UserManager(BaseUserManager):
    """Миксин для управления пользователями"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя"""

    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    email = models.EmailField(_("email address"), unique=True)
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    USER_TYPE = (
        ('shop', 'Магазин'),
        ('buyer', 'Покупатель'),
    )

    type = models.CharField(choices=USER_TYPE, max_length=5, default='buyer', verbose_name='Тип пользователя')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)


class ConfirmEmailToken(models.Model):
    """Токен подтверждения Email"""

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)


class Shop(models.Model):
    """Магазин"""

    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')

    state = models.BooleanField(default=True, verbose_name='Принимает заказы')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Товарная категория"""

    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True, verbose_name='Магазины')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""

    name = models.CharField(max_length=80, verbose_name='Название')

    category = models.ForeignKey(Category, related_name='products', blank=True, on_delete=models.CASCADE,
                                 verbose_name='Категория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """Информация о товаре"""

    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID')

    product = models.ForeignKey(Product, verbose_name='Товар', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)

    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(verbose_name='Количество')

    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Информация о товарах'

        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]

    def __str__(self):
        return str(self.external_id)


class Parameter(models.Model):
    """Название параметра"""

    name = models.CharField(max_length=64, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имен параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """Параметр товара"""

    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE, verbose_name='Информация о товаре')

    parameter = models.ForeignKey(Parameter, related_name='product_parameters', blank=True, on_delete=models.CASCADE,
                                  verbose_name='Параметр')

    value = models.CharField(max_length=128, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры товаров'

        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.product_info.model} | {self.parameter.name}'


class Contact(models.Model):
    """Контакт клиента"""

    user = models.ForeignKey(User, related_name='contacts', blank=True, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    phone = models.CharField(max_length=32, verbose_name='Телефон')

    city = models.CharField(max_length=32, verbose_name='Город')
    street = models.CharField(max_length=64, verbose_name='Улица')
    house = models.CharField(max_length=16, verbose_name='Дом')

    structure = models.CharField(max_length=16, blank=True, verbose_name='Корпус')
    building = models.CharField(max_length=16, blank=True, verbose_name='Строение')
    apartment = models.CharField(max_length=16, blank=True, verbose_name='Квартира')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    """Заказ"""

    user = models.ForeignKey(User, related_name='orders', blank=True, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    ORDER_STATUS = (
        ('cart', 'Статус корзины'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )

    status = models.CharField(choices=ORDER_STATUS, max_length=16, verbose_name='Статус заказа')
    contact = models.ForeignKey(Contact, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Контакт')

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user.email} | order_id {self.id}'


class OrderItem(models.Model):
    """Позиция в заказе"""

    order = models.ForeignKey(Order, related_name='ordered_items', blank=True, on_delete=models.CASCADE,
                              verbose_name='Заказ')

    product_info = models.ForeignKey(ProductInfo, related_name='ordered_items', blank=True, on_delete=models.CASCADE,
                                     verbose_name='Информация о товаре')

    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Заказанные позиции'

        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item')
        ]
