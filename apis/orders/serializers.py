from rest_framework import serializers

from apis.cart.models import Cart
from apis.orders.models import Order, OrderItem, OrderPayment


class CheckoutSerializer(serializers.Serializer):
    def create(self, validated_data):
        user = self.context['request'].user

        # Fetch the user's cart
        try:
            cart = Cart.objects.get(user=user)
            cart_items = cart.cart_item.all()

            if not cart_items.exists():
                raise serializers.ValidationError("Your cart is empty.")

            # Calculate total amount
            total_amount = sum(item.price for item in cart_items)

            # Create the order
            order = Order.objects.create(user=user, total_amount=total_amount, status='completed')

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(order=order, course=item.course, price=item.price)

            # Clear the cart after checkout
            cart_items.delete()

            return order

        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart does not exist.")


class OrderItemListSerializer(serializers.ModelSerializer):
    # total_amount = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'course', 'price'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course_title', 'price']


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_uuid', 'total_amount', 'status', 'items']

    def get_items(self, obj):
        return [{'course': item.course.title, 'price': item.price} for item in obj.items.all()]


class OrderPaymentSerializer(serializers.ModelSerializer):
    receipt_url = serializers.ImageField(source='receipt', use_url=True, read_only=True)

    class Meta:
        model = OrderPayment
        fields = ['id', 'order', 'receipt', 'receipt_url', 'is_approved']
        read_only_fields = ['is_approved']


class OrderApprovalSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_payment = OrderPaymentSerializer(many=True, read_only=True)  # Matches related_name in the model

    class Meta:
        model = Order
        fields = ['id', 'order_uuid', 'total_amount', 'status', 'items', 'order_payment']