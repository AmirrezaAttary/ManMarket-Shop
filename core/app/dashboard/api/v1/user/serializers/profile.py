# app/accounts/serializers.py
from rest_framework import serializers
from app.accounts.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'first_name',
            'last_name',
            'birth_date',
            'image',
            'phone_number',
        ]
        read_only_fields = ['id', 'phone_number']