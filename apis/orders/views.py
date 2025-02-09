from django.shortcuts import render
from django.db.models import Count
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated

from apis.core.utlis import api_response
from apis.courses.serializers import CourseListSerializer
from apis.orders.models import Order, OrderPayment
from apis.orders.serializers import CheckoutSerializer, OrderListSerializer, OrderItemListSerializer, \
    OrderPaymentSerializer, OrderApprovalSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser


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


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            orders = Order.objects.get(user=user).order_by('-modified_on')
            return orders.items.all()  # Fetch all items related to the user's cart
        except Order.DoesNotExist:
            return []

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            orders = Order.objects.filter(user=user)

            if orders.exists():
                data = []
                for order in orders:
                    order_data = {
                        'order_id': order.id,
                        'order_uuid': order.order_uuid,
                        'order_status': order.get_status_display(),
                        'total_amount': order.total_amount,
                        'order_date': order.created_on,
                        'total_items': order.items.all().count(),
                        'items': OrderItemListSerializer(order.items.all(), many=True).data
                    }
                    data.append(order_data)

                status_counts = orders.values('status').annotate(count=Count('status'))

                # Create a mapping of raw status to display name
                status_display_mapping = dict(Order._meta.get_field('status').choices)

                # Format status counts to use display names
                formatted_status_counts = {
                    status_display_mapping.get(status_count['status'], status_count['status']): status_count['count']
                    for status_count in status_counts
                }

                return api_response(
                    status="success",
                    message="Orders retrieved successfully.",
                    data={
                        "order_count": orders.count(),
                        "status_count": status_counts,
                        "orders": data
                    },
                    http_status=status.HTTP_200_OK,
                )
            else:
                return api_response(
                    status="success",
                    message="No orders found.",
                    data={
                        "order_count": 0,
                        "status_count": {},
                        "orders": []
                    },
                    http_status=status.HTTP_200_OK,
                )

        except Exception as e:
            print('exception', e)
            return api_response(
                status="error",
                message="An unexpected error occurred while retrieving orders.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderPaymentViewSet(viewsets.ModelViewSet):
    queryset = OrderPayment.objects.all()
    serializer_class = OrderPaymentSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can interact

    def get_queryset(self):
        # Return payments related to the current user's orders
        return OrderPayment.objects.filter(order__user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Custom creation logic if needed
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()  # Save the payment instance

            order = payment.order
            order.status = 'pending_acceptance'
            order.save()
            # self.perform_create(serializer)
            return api_response(
                status="success",
                message="Payment submitted successfully.",
                data=serializer.data,
                http_status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print('exception', e)
            return api_response(
                status="error",
                message="An unexpected error occurred while payment submission.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            # self.perform_update(serializer)

            payment = serializer.save()

            if payment.is_approved:
                payment.order.status = 'accepted'
                payment.order.save()

            return api_response(
                status="success",
                message="Payment updated successfully.",
                data=serializer.data,
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            print('exception', e)
            return api_response(
                status="error",
                message="An unexpected error occurred on payment update.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        try:
            payment = self.get_object()
            payment.is_approved = True
            payment.save()
            return api_response(
                status="success",
                message="Payment approved successfully.",
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            print('exception', e)
            return api_response(
                status="error",
                message="An unexpected error occurred on payment approval.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to retrieve orders for approval.
    """
    queryset = Order.objects.filter(status='pending_acceptance')
    serializer_class = OrderApprovalSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            orders = self.get_queryset()
            serializer = self.get_serializer(orders, many=True)

            return api_response(
                status="success",
                message="Pending acceptance orders retrieved successfully.",
                data=serializer.data,
                http_status=status.HTTP_200_OK
            )

        except Exception as e:
            return api_response(
                status="error",
                message="An unexpected error occurred while retrieving.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )