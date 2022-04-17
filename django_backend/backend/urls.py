from django.urls import path

from backend.views import RegisterAccount, ConfirmAccount, ContactView, AccountDetails, CartView, OrderView
from backend.views import SellerUpdateCatalog, SellerState, ShopView, SellerOrderView
from backend.views import ProductInfoRetrieve, ProductInfoView, CategoryView

from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'backend'

urlpatterns = [
    # Регистрация пользователя и подтверждение электронной почты
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),

    # Аутентификация пользователя и обновление токена доступа
    path('user/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/login/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    # Сброс пароля аккаунта
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),

    # CRUD для контактов пользователя
    path('user/contacts', ContactView.as_view(), name='user-contacts'),
    path('user/details', AccountDetails.as_view(), name='user-details'),

    # Обновление каталога и статуса продавца, работа с заказами
    path('seller/update', SellerUpdateCatalog.as_view(), name='seller-update-catalog'),
    path('seller/state', SellerState.as_view(), name='seller-state'),
    path('seller/orders', SellerOrderView.as_view(), name='seller-orders'),

    # Просмотр каталога товаров
    path('catalog/products/<int:pk>', ProductInfoRetrieve.as_view(), name='product-info'),
    path('catalog/products', ProductInfoView.as_view(), name='products'),
    path('catalog/categories', CategoryView.as_view(), name='categories'),
    path('catalog/shops', ShopView.as_view(), name='shops'),

    # CRUD для работы с корзиной покупателя, получение и оформление заказов
    path('cart', CartView.as_view(), name='cart'),
    path('order', OrderView.as_view(), name='order'),
]
