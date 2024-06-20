from rest_framework import serializers
from .models import Product, Customer, Orders, OrderItem, CartItem
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'price', 'category']

class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Make password optional for update
    confirm_password = serializers.CharField(write_only=True, required=False)  # Make confirm_password optional for update

    class Meta:
        model = Customer
        fields = ['username', 'customer_name', 'email', 'phone_number', 'address', 'city', 'state', 'password', 'confirm_password', 'profile_picture','last_login']

    def validate(self, data):
        if 'password' in data and data['password'] != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        
        # Create corresponding User instance
        User.objects.create_user(username=customer.username, email=customer.email, password=password)
        return customer

    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)

        # Update the instance with the remaining validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If a password is provided, set the new password
        if password:
            instance.set_password(password)

        instance.save()
        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Include the product details

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)  # Use OrderItemSerializer to include nested products
    shipping_status = serializers.ChoiceField(choices=Orders.SHIPPING_STATUS_CHOICES, read_only=True)

    class Meta:
        model = Orders
        fields = ['id', 'user', 'items', 'total_amount', 'created_at', 'shipping_status']

    def update(self, instance, validated_data):
        # Only allow admin users to update shipping_status
        if self.context['request'].user.is_staff:
            instance.shipping_status = validated_data.get('shipping_status', instance.shipping_status)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"detail": "Only admin users can update shipping status."})


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Include the product details

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

