from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.dispatch import receiver, Signal
from backend.models import ConfirmEmailToken

from django_rest_passwordreset.signals import reset_password_token_created


new_user_registered = Signal('user_id')


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
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


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """Отправляем письмо для сброса пароля"""

    message = f'Ваш токен для сброса пароля: {reset_password_token.key}'

    msg = EmailMultiAlternatives(
        # title:
        'Password Reset Token',
        # message:
        message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )

    msg.send()
