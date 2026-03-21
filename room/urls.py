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
    path('products/', views.Products_view, name='products'),
    path('orders/', views.orders_page, name='orders'),
    #-------------------- public url
    path('api/getproducts', views.GetAllProducts, name='getProducts'),
    path('api/products/add', views.create_Products, name='setProducts' ),
    path('api/product/<slug:slug>', views.getProduct, name='getProduct'),
    path('api/customer/signup', views.CreateUser, name='signup'),
    path('api/customer/login', views.LoginUser, name='login')
]