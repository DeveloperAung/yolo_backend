from django.urls import path
from .views import AddToCartView, FetchUserCartView, DeleteCartItemView, DeleteAllCartItemView

urlpatterns = [
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('', FetchUserCartView.as_view(), name='fetch-user-cart'),
    path('delete/<int:cart_item_id>/', DeleteCartItemView.as_view(), name='delete-cart-item'),
    path('delete_all/', DeleteAllCartItemView.as_view(), name='delete-all-cart-item'),
]
