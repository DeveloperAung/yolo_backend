from rest_framework import serializers

from apis.cart.models import Cart
from apis.courses.models import Course
from apis.courses.serializers import LessonSerializer, CourseCreateSerializer, CourseListSerializer
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
            order = Order.objects.create(user=user, total_amount=total_amount, status='pending_upload')

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(order=order, course=item.course, price=item.price)

            # Clear the cart after checkout
            cart_items.delete()

            return order

        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart does not exist.")


class OrderItemListSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    # total_amount = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'course', 'price'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'course_title', 'price']


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


class CourseListSerializer(serializers.ModelSerializer):
    instructor_username = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    demo_video = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    in_cart = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'recommendation', 'total_duration', 'description', 'modified_on',
            'instructor_username', 'cover_image', 'demo_video', 'is_on_sale', 'price', 'sale_price',
            'in_cart', 'is_purchased', 'lessons'
        ]

    def get_instructor_username(self, obj):
        return obj.instructor.username if obj.instructor else "Unknown Instructor"

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
        return ""

    def get_demo_video(self, obj):
        return obj.demo_video.url if obj.demo_video else ""

    def get_price(self, obj):
        return float(obj.price) if obj.price else 0.0

    def get_sale_price(self, obj):
        return float(obj.sale_price) if obj.sale_price else 0.0

    def get_is_on_sale(self, obj):
        return obj.is_on_sale if obj.is_on_sale is not None else False

    def get_in_cart(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return obj.enrolled_course.filter(order__user=request.user, order__status='accepted').exists()
        return False  # Default to False if not authenticated

    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return obj.enrolled_course.filter(order__user=request.user, order__status='accepted').exists()
        return False  # Default to False if not authenticated
