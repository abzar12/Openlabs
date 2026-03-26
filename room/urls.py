from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('getAllUsers/', views.getAlluser_view, name='users'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('dashboard/', views.dashHome, name="dashboard"),
    path('add-product/', views.AddProduct, name='addProduct'),
    path('products/', views.Products_view, name='rooms'),
    path('edit/room/<int:room_id>', views.EditRoom_view, name='editRoom'),
    path('orders/', views.orders_page, name='orders'),
    path('order/delete/<int:order_id>', views.delete_Order, name='delete_order'),
    path('order/confirmed/<int:order_id>', views.EditStatusOrder_view, name='edit_status'),
    #-------------------- public url
    path('api/getproducts', views.GetAllProducts, name='getProducts'),
    path('api/products/add', views.create_Products, name='setProducts' ),
    path('api/product/<slug:slug>/', views.getProduct, name='getProduct'),
    path('api/customer/signup', views.CreateUser, name='signupApi'),
    path('api/refreshtk', views.getRefreshToken, name='refreshToken'),
    path('api/logout', views.Logout, name='logoutApi'),
    path('api/me', views.getCurrentUser, name='getUser'),
    path('api/customer/login', views.LoginUser, name='loginApi'),
    path('api/checkOut/', views.CreateOrders, name='createOrder'),
]