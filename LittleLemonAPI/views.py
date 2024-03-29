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

        total_price = sum(cart_item.price for cart_item in user_cart)

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


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Manager").exists():
            return Order.objects.all()
        else:
            return Order.objects.filter(user=user)

    def get(self, request, *args, **kwargs):
        order = self.get_object()

        if order.user != request.user:
            return Response(
                {"message": "You don't have permission to view this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        order = self.get_object()

        if (
            not request.user.groups.filter(name="Manager").exists()
            and order.user != request.user
        ):
            return Response(
                {"message": "You don't have permission to update this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):

        return self.put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()

        if (
            not request.user.groups.filter(name="Manager").exists()
            or order.user != request.user
        ):
            return Response(
                {"message": "You don't have permission to delete this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.delete()
        return Response(
            {"message": "Order deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# USER GROUP MANAGEMENT VIEWS
