from django.urls import path, include
from .views import MenuItemsListView,MenuItemsDetailView

urlpatterns = [
    path('menu-items/', MenuItemsListView.as_view(), name='menu-items-list'),
    path('menu-items/<int:pk>/', MenuItemsDetailView.as_view(), name='item-detail')
]