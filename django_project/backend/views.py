from django.contrib.auth.password_validation import validate_password

from django.http import JsonResponse
from rest_framework.views import APIView

from backend.serializers import UserSerializer


class RegisterAccount(APIView):
    """Регистрация клиента"""

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

                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
