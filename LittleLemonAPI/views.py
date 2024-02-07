from rest_framework import generics, permissions
from .serializers import *


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

# ORDER MANAGEMENT VIEWS
# class OrderItemsListView(generics.ListAPIView):

# USER GROUP MANAGEMENT VIEWS
