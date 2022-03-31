from rest_framework import serializers

from backend.models import Contact, User


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'user', 'phone', 'city', 'street', 'house', 'structure', 'building', 'apartment')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'contacts')
        read_only_fields = ('id',)
