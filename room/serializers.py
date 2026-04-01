from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Room, User, Orders, OrderItems, Amenities
class AmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Amenities
        fields = ['id', 'name']
class ProductSerializers(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    amenities = AmenitiesSerializer(many=True)
    class Meta:
        model = Room
        fields = ['uuid', 'slug', 'user_email' , 'title',  'category', 'price', 'promot_price', 'location', 
                  'description', 'amenities','guest_number', 'bedroom', 'bathroom' , 'images', 'created_at']
        
    # ---------------------Register serializer
class RegistrationSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'localization', 'password', 'confirm_password']
        extra_kwargs = {
            'role': {'read_only': True}  # Optional: prevent users from setting roles directly
        }
    def validate(self, data):
        if data['password'] != data['confirm_password'] :
            raise serializers.ValidationError("Passwords do not match")
        return data
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        user = User.objects.create_user(
            username= validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email = validated_data['email'],
            phone_number=validated_data['phone_number'],
            localization=validated_data['localization'],
            password= validated_data['password']
        )
        return user
    # ---------------------login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        user = authenticate(
            email = data['email'],
            password= data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
    
class OrderItemsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ['room']
        
class OrdersSerializer(serializers.ModelSerializer):
    orderitems = OrderItemsCreateSerializer(many=True)
    
    class Meta:
        model = Orders
        fields = '__all__'  # Use only the fields you need
        read_only_fields = ['total_amount', 'user']  # Read-only fields
    
    def create(self, validated_data):
        user = self.context['user']  # Extract user from context
        total_amount = self.context['total_amount']  # Extract total_amount from context
        orderitems_data = validated_data.pop('orderitems')  # Extract orderitems from validated data
        
        # Use transaction.atomic() for database integrity
        with transaction.atomic():
            order = Orders.objects.create(
                user=user,
                total_amount=total_amount
            )

            for item_data in orderitems_data:
                room = item_data.get('room')  # Get the room from the item
                if not room:
                    continue  # Skip invalid items
                OrderItems.objects.create(
                    order=order,
                    room=room,
                    amount=room.price  # Assign room price as the amount
                )

        return order

class OrderItemsSerializer(serializers.ModelSerializer):
    order = OrdersSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    class Meta:
        model= OrderItems
        fields= ['id', 'order', 'room', 'amount']
        read_only_fields = ['amount', 'order']  # ✅ important