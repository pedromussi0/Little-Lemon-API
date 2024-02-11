from django.urls import path, include
from .views import *

urlpatterns = [
    path("menu-items/", MenuItemsListView.as_view(), name="menu-items-list"),
    path("menu-items/<int:pk>/", MenuItemsDetailView.as_view(), name="item-detail"),
    path("cart/menu-items/", CartMenuItemsView.as_view(), name="cart-menu-items"),
    path("orders/", OrdersListView.as_view(), name="orders-list"),
]
