from django.urls import path
from .views import AddToCartView, FetchUserCartView

urlpatterns = [
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('', FetchUserCartView.as_view(), name='fetch-user-cart'),
]
