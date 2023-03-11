from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'inn', 'money_amount']


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(min_value=0, decimal_places=2, max_digits=64)
    sender = serializers.IntegerField(min_value=0)
    inns = serializers.ListSerializer(child=serializers.IntegerField(min_value=0))
