from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, CarouselViewSet

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'carousels', CarouselViewSet, basename='carousel')

urlpatterns = [
    path('', include(router.urls)),
]
