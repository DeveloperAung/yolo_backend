from rest_framework import serializers

from apis.cart.models import Cart
from apis.orders.models import Order, OrderItem


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
