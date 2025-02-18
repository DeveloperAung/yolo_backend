from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Business, Carousel, BankInfo, PaymentBankInfo


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'  # Includes all fields in Business


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'  # Includes all fields in Carousel


class BankInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankInfo
        fields = '__all__'


class PaymentBankInfoSerializer(serializers.ModelSerializer):
    bank = BankInfoSerializer(read_only=True)  # Full bank details in response
    bank_id = serializers.PrimaryKeyRelatedField(
        queryset=BankInfo.objects.all(), source='bank', write_only=True
    )  # Accept bank_id in API requests

    class Meta:
        model = PaymentBankInfo
        fields = '__all__'

    def validate(self, data):
        if 'account_no' in data and not data['account_no'].isdigit():
            raise ValidationError({"account_no": "Account number must be numeric."})

        if 'name' in data and len(data['name']) < 3:
            raise ValidationError({"name": "Name must be at least 3 characters long."})

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            raise ValidationError({"error": str(e)})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise ValidationError({"error": str(e)})