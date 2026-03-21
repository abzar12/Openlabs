from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Room, Amenities
# Register your models here.
@admin.register(User)

class CustomerUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("phone_number",)}),
    )
    search_fields= ['username','first_name', 'last_name', 'email', 'phone_number']
    
class ProductsAdmin(admin.ModelAdmin):
    list_display=['title', 'category', 'price', 'location', 'description', 'images', 'created_at' , 'updated']
    search_fields= ['category', 'product', 'user', 'price', 'created_at']
    list_filter = ['category', 'product', 'user', 'price', 'created_at']
admin.site.register( Room)
admin.site.register(Amenities)

    
admin.site.site_header = "Sissoko-room"
admin.site.site_title = "abzar camarar"
    