from rest_framework import serializers
from .models import Business, Carousel


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'  # Includes all fields in Business


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'  # Includes all fields in Carousel
