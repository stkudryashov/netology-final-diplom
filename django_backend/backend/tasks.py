from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from backend.models import ConfirmEmailToken, User, Order

from celery import shared_task


@shared_task
def new_user_registered_task(user_id):
    """Отправляем письмо с подтверждением почты"""

    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    message = f'Ваш токен для подтверждения почты: {token.key}'

    msg = EmailMultiAlternatives(
        # title:
        'Confirmation Token',
        # message:
        message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email])

    msg.send()
    return True


def new_order_task(user_id, status):
    """Отправляем письмо при изменении статуса заказа"""

    user = User.objects.get(id=user_id)

    order_status = dict(Order.ORDER_STATUS)
    message = f'Новый статус заказа: {order_status[status]}'

    msg = EmailMultiAlternatives(
        # title:
        'Обновление статуса заказа',
        # message:
        message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )

    msg.send()
    return True
