from rest_framework import serializers
from .models import *  # Import your MenuItem model
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]


class CartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ["id", "menuitem", "quantity", "unit_price", "price"]
        read_only_fields = ["price"]

    def create(self, validated_data):
        # Calculate the price based on MenuItem's price and quantity
        menuitem = validated_data["menuitem"]
        quantity = validated_data["quantity"]
        unit_price = menuitem.price
        validated_data["unit_price"] = unit_price
        validated_data["price"] = unit_price * quantity

        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    cart_items = CartSerializer(many=True, read_only=True)  # Corrected source

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "delivery_crew",
            "status",
            "total",
            "date",
            "cart_items",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "menuitem", "quantity", "unit_price", "price"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
