#  serializers 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializers, RegistrationSerializers, LoginSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
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
# def Orders_view(request):
@staff_member_required(login_url='login')
def orders_view(request):
    recent_orders = Orders.objects.order_by('created_at')[:10]
    return render(request, 'dashboard.html', {"orders": recent_orders})

@staff_member_required(login_url='login')
def orders_page(request):
    orders = Orders.objects.all()
    return render(request, 'orderPage.html', {'orders': orders})
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
            max_age=5*60     # 5 minutes
        )

        # Optional: Set refresh token as well
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=False,
            max_age=24*60*60
        )
        return response
    return Response(serializers.errors, status=status.HTTP_401_UNAUTHORIZED)

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
#---------------------------------- create Products 
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

@api_view(['GET'])
def getProduct(request, slug):
    product = get_object_or_404(Room, slug=slug)
    serializer_class = ProductSerializers(product)
    return Response(serializer_class.data, status=status.HTTP_200_OK)