from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, CarouselViewSet, BankInfoViewSet, PaymentBankInfoViewSet

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'carousels', CarouselViewSet, basename='carousel')
router.register(r'bank-info', BankInfoViewSet, basename='bank-info')
router.register(r'payment-bank-info', PaymentBankInfoViewSet, basename='payment-bank-info')


urlpatterns = [
    path('', include(router.urls)),
]
