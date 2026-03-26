from rest_framework import serializers
from django.contrib.auth import authenticate
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
        
class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model= OrderItems
        fields= ['amount', 'order', 'room']
        read_only_fields = ['amount', 'order']  # ✅ important

        
class OrdersSerializer(serializers.ModelSerializer):
    orderitems = OrderItemsSerializer(many=True, read_only=True)
    class Meta:
        model = Orders
        fields= ['user', 'orderitems', 'total_amount'] # for creating ording we just need room(fk), amount and user(fk)
        read_only_fields = ['total_amount', 'user']  # ✅ important
        
    def create(self, validated_data):
        user = self.context['user']  # user passed via context
        orderitems_data = self.context['orderitems_data']  # items passed via context

        # calculate total_amount
        total_amount = sum(item['room'].price for item in orderitems_data)
        order = Orders.objects.create(user=user, total_amount=total_amount)

        # create OrderItems
        for item_data in orderitems_data:
            OrderItems.objects.create(
                order=order,
                room=item_data['room'],
                amount=item_data['room'].price
            )

        return order

            
        