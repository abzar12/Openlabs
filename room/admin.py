from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Room, Amenities,Orders, OrderItems
# Register your models here.

@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("phone_number",)}),
    )
    # list_display= ['role']
    search_fields= ['username', 'first_name', 'last_name', 'role', 'email', 'phone_number']
    
class ProductsAdmin(admin.ModelAdmin):
    def display_amenities(self, obj):
        return ", ".join([a.name for a in obj.amenities.all()])

    display_amenities.short_description = "Amenities"
    list_display=['title', 'category', 'price', 'display_amenities', 'location', 'images', 'created_at' , 'updated']
    search_fields= ['category', 'title', 'user', 'price', 'created_at']
    list_filter = ['category', 'title', 'user', 'price', 'created_at']
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'reference', 'total_amount', 'payment_method', 'payment_status', 'order_status', 'created_at']
    search_fields = ['order_number', 'user', 'created_at', 'payment_status', 'order_status']
    list_filter= ['order_number', 'user', 'created_at', 'payment_status', 'order_status']
class OrderItemsAdmin(admin.ModelAdmin):
    list_display=['order', 'room', 'amount']
    search_fields =['order', 'room', 'amount']
    list_filter= ['order', 'room', 'amount']
admin.site.register(Room, ProductsAdmin)
admin.site.register(Amenities)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderItems, OrderItemsAdmin)

    
admin.site.site_header = "Sissoko-room"
admin.site.site_title = "abzar camarar"
    