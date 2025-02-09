from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckoutView, OrderListAPIView, OrderPaymentViewSet, OrderApprovalViewSet

router = DefaultRouter()
router.register(r'order-payments', OrderPaymentViewSet, basename='order-payment')
router.register(r'pending-acceptance-orders', OrderApprovalViewSet, basename='pending-acceptance-orders')

urlpatterns = [
    path('payment/', include(router.urls)),
    path('acceptance/', include(router.urls)),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', OrderListAPIView.as_view(), name='order_list'),
]
