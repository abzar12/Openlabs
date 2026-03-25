#  serializers 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import ProductSerializers, RegistrationSerializers, LoginSerializer, UserSerializer, OrdersSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

# ---------------------
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterFrom, ProductForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
# =--------------import model--------
from .models import Room, Orders, User, Amenities
# Create your views here.
#  -----------------------------------Dashboard view---------------------------------------

#---------------------------- get refresh token
@api_view(['POST'])
def getRefreshToken(request):
    refresh = request.COOKIES.get('refresh_token')
    
    if not refresh:
        return Response({"error": "Unauthorize"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        refresh_token=RefreshToken(refresh)
        access_token = str(refresh_token.access_token)
        
        response = Response({"message": "New Access token given"})
        
        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=15*60,
            httponly=True,
            samesite='Lax',
            secure=False
            )
        return response
    except Exception:
        return Response({"error": "Invalid Refresh Token"}, status.HTTP_401_UNAUTHORIZED)
          
def register_view(request):
    if request.method == "POST":
        form = RegisterFrom(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
          print("FORM ERRORS:", form.errors) 
    else:
        form = RegisterFrom()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    # if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST or None)
        
        if request.method == "POST" :
            if form.is_valid():
                user = form.get_user()
                login(request, user) # this will create session
                return redirect("dashboard")
            else:
                print(form.errors)
        return render(request, 'login.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')
@staff_member_required(login_url='login')
def dashHome(request):
    return render(request, "dashHome.html")
# --------------get all admin user
@staff_member_required(login_url='login')
def getAlluser_view(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})
# def Orders_view(request): for dashboard
@staff_member_required(login_url='login')
def orders_view(request):
    recent_orders = (
        Orders.objects
        .exclude(order_status='archived')
        .order_by('-created_at')
        .prefetch_related('orderitems__room') 
        )[:50] # fetch related items and rooms
    return render(request, 'dashboard.html', {"orders": recent_orders})

@staff_member_required(login_url='login')
def orders_page(request):
    orders = (
        Orders.objects
        .exclude(order_status='archived')
        .order_by('-created_at')
        .prefetch_related('orderitems__room') 
        )[:100]
    return render(request, 'orderPage.html', {'orders': orders})
#  delete un orders 
def delete_Order(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    print("POST REQUEST")  # 👈 add this
    order.order_status = 'archived'
    order.save()
    return redirect('orders')
# confirm un order 
def confirmOrder_view(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    order.order_status = 'confirmed'
    order.save()
    return redirect('orders')
# Products view -----------
@staff_member_required(login_url='login')
def AddProduct(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            product.save_m2m()
            return redirect("addProduct")
        else:
            print("Form errors:", form.errors)
            print(form.errors)
    else:
        form = ProductForm()
    return render(request, 'createProduct.html', {'form': form})
# -------Get All the products 
@staff_member_required(login_url='login')
def Products_view(request):
    products = Room.objects.all()
    # room = Amenities.objects.all()
    return render(request, 'products.html', {'products': products})
            
#  -----------------------------------Public view---------------------------------------

#---------------------------------- create user 

@api_view(['POST'])
def CreateUser(request):
    serializers = RegistrationSerializers(data=request.data)
    if serializers.is_valid():
        serializers.save()
        return Response({
            "message": "User registered successfully",
            "response": serializers.data,
            "status":status.HTTP_201_CREATED
        })
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#---------------------------------- login user 
@api_view(['POST'])
def LoginUser(request):
    serializers = LoginSerializer(data=request.data)
    
    if serializers.is_valid():
        user = serializers.validated_data['user']
        user_data = UserSerializer(user).data
        # create tokens for user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "message": "Login successful",
            "user": user_data,
            "status": status.HTTP_202_ACCEPTED
        })
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            samesite='Lax',  # or 'Strict'
            secure=False,    # True if using HTTPS
            max_age=15*60     # 15 minutes
        )

        # Optional: Set refresh token as well
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=False,
            max_age=24*60*60*7
        )
        return response
    return Response(serializers.errors, status=status.HTTP_401_UNAUTHORIZED)

# ---------------------------------Logout
@api_view(['POST'])
def Logout(request):
    logout(request)
    return Response({"message": "User Logged-Out"})

#---------------------------- get current user
@api_view(['GET'])
def getCurrentUser(request):
    token = request.COOKIES.get('access_token')
    if not token:
        return Response({'error': "Not Authenticated"}, 401)
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']

        user = User.objects.get(id=user_id)

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role":user.role,
            "firstname":user.first_name,
            "lastname":user.last_name,
            "phone":user.phone_number,
            "localization":user.localization,
        })
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    
#---------------------------------- create Products 
@api_view(['GET'])
def GetAllProducts(request):
    room_type = request.query_params.get('type', "All")
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 50))
    
    product = Room.objects.all()
    if room_type != "All":
        product = product.filter(category=room_type)
    
     # Pagination manually
    start = (page - 1) * limit
    end = start + limit
    data = product[start:end]
    
    serialiser = ProductSerializers(data, many=True, context={'request': request})
    return Response(serialiser.data, status=status.HTTP_200_OK)

# ---------------------------------Create new product
@api_view(['POST'])
def create_Products(request):
    serializer = ProductSerializers(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user) #insign logged in user
        return Response({
            "message": "User registered successfully",
            "response": serializer.data,
            "status":status.HTTP_201_CREATED
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------getProduct product by slug
@api_view(['GET'])
def getProduct(request, slug):
    product = get_object_or_404(Room, slug=slug)
    serializer_class = ProductSerializers(product)
    return Response(serializer_class.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def CreateOrders(request):
    token = request.COOKIES.get('access_token')
    print(request.COOKIES.get('access_token'))
    if not token:
        return Response({'error': "Not Authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, TokenError):
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    if not isinstance(data, list):
        return Response({'error': 'Items must be a list'}, status=status.HTTP_400_BAD_REQUEST)
    items_for_serializer = []
    for item in data:
        uuid = item.get('uuid')
        if not uuid:
            return Response({'error': 'UUID is required'}, status=status.HTTP_400_BAD_REQUEST)

        room = Room.objects.filter(uuid=uuid).first()
        if not room:
            return Response({'error': f'Room {uuid} not found'}, status=status.HTTP_404_NOT_FOUND)

        items_for_serializer.append({
            'room': room
        })
    serializer = OrdersSerializer(data={}, context={'user': user, 'orderitems_data': items_for_serializer})
    if serializer.is_valid():
        order = serializer.save()
        return Response(OrdersSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
        
         