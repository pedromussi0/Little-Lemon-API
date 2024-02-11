from datetime import date

from rest_framework import generics, permissions, status
from .serializers import *
from rest_framework.response import Response
from .models import *


# MENU ITEMS VIEWS


class MenuItemsListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MenuItemsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# CART MANAGEMENT VIEWS
class CartMenuItemsView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        user = request.user
        request.data["user"] = user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ORDER MANAGEMENT VIEWS

# Got error : Cart has no attribute objects.
# i need to reference the cart serializer in the order list view.
# The logic looks fine


class OrdersListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Manager").exists():
            return Order.objects.all()

        return Order.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        user_cart = Cart.objects.filter(user=request.user)

        if not user_cart:
            return Response(
                {"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate the total price of the order
        total_price = sum(cart_item.price for cart_item in user_cart)

        # Create a new order
        order = Order.objects.create(
            user=request.user, total=total_price, status=False, date=date.today()
        )

        order_items_data = []
        for cart_item in user_cart:
            order_items_data.append(
                {
                    "order": order.id,
                    "menuitem": cart_item.menuitem.pk,
                    "quantity": cart_item.quantity,
                    "unit_price": cart_item.unit_price,
                    "price": cart_item.price,
                }
            )

        order_serializer = OrderItemSerializer(data=order_items_data, many=True)
        if order_serializer.is_valid():
            order_serializer.save()
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_cart.delete()

        return Response(
            {"message": "Order created successfully"}, status=status.HTTP_201_CREATED
        )


# USER GROUP MANAGEMENT VIEWS
