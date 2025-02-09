from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apis.cart.models import Cart, CartItem
from apis.cart.serializers import AddToCartSerializer, CartItemSerializer
from apis.core.utlis import api_response


class AddToCartView(generics.CreateAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can add to cart

    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer = self.get_serializer(data=request.data, context={'request': request})
        # print('data', request.data)
        try:
            if serializer.is_valid():
                cart_item = serializer.save()

                return api_response(
                    status="success",
                    message=f"'{cart_item.course.title}' added to cart.",
                    data={
                        "course": cart_item.course.title,
                        "price": str(cart_item.price)
                    },
                    http_status=status.HTTP_201_CREATED
                )
            else:
                return api_response(
                    status="error",
                    errors="some data has an issue",
                    http_status=status.HTTP_406_NOT_ACCEPTABLE
                )
        except Exception as e:
            # logger.exception("An unexpected error occurred during logout.")
            print('exception', e)
            return api_response(
                status="error",
                message="An unexpected error occurred.",
                errors={"details": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FetchUserCartView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            cart = Cart.objects.get(user=user)
            return cart.cart_item.all()  # Fetch all items related to the user's cart
        except Cart.DoesNotExist:
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return api_response(
                status="success",
                message="Your cart is empty",
                data=[]
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status="success",
            message="Data retrieve successfully",
            data=serializer.data
        )


class DeleteCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        cart_item_id = kwargs.get('cart_item_id')

        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(cart=cart, id=cart_item_id)
            cart_item.delete()

            return api_response(
                status="success",
                message="Course removed from cart successfully.",
            )
        except Cart.DoesNotExist:
            return api_response(
                status="error",
                message="Cart does not exist.",
                http_status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return api_response(
                status="error",
                message="Course not found in cart.",
                http_status=status.HTTP_404_NOT_FOUND
            )


class DeleteAllCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
            cart.cart_item.all().delete()  # 🔥 Delete all items related to the user's cart

            return api_response(
                status="success",
                message="All courses removed from cart successfully."
            )
        except Cart.DoesNotExist:
            return api_response(
                status="error",
                message="Cart does not exist.",
                http_status=status.HTTP_404_NOT_FOUND
            )