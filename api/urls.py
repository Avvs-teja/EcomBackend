from django.urls import path
from . import views
from .views import request_password_reset, reset_password

urlpatterns = [
    path('', views.hello_user, name='hello_user'),
    path('getProducts/', views.get_products, name='get_products'),
    path('register/', views.register_customer, name='register_customer'),
    path('login/', views.login_customer, name='login_customer'),
    path('customer/', views.CustomerDetail.as_view(), name='customer_detail'),
    path('logout/', views.logout, name='logout'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('cart/', views.manage_cart, name='manage_cart'),  # Added single URL for cart management
    path('cart/<int:product_id>/', views.manage_cart, name='manage_cart_with_product'),  # Added single URL for cart management with product
    path('place-order/', views.place_order, name='place_order'),
    path('user-orders/', views.UserOrderList.as_view(), name='user_orders'),
    path('order/<int:pk>/', views.OrderDetail.as_view(), name='order_detail'),
    
]
