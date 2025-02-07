from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apis.core.utlis import api_response
from apis.orders.serializers import CheckoutSerializer


class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            order = serializer.save()
            return api_response(
                status="success",
                message="Checkout successful! Order created.",
                data={"order_id": order.id, "total_amount": order.total_amount}
            )

        return api_response(
            status="error",
            message="Checkout failed.",
            errors=serializer.errors,
            http_status=status.HTTP_400_BAD_REQUEST
        )
