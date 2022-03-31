from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.dispatch import receiver, Signal
from backend.models import ConfirmEmailToken


new_user_registered = Signal('user_id')


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """Отправляем письмо с подтверждением почты"""

    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    message = f'Ваш токен для подтверждения почты: {token.key}'
    msg = EmailMultiAlternatives(f'Confirmation Token', message, settings.EMAIL_HOST_USER, [token.user.email])

    msg.send()
