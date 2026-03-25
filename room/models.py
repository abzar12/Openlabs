import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable= False )
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=200, unique= True)
    localization= models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=200, default='customer', null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 
    
    def __str__(self):
        return  self.email or self.phone_number or str(self.user_id)

class Amenities(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.name
    
class Room(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms')
    slug = models.SlugField(unique=True, blank= True)
    title = models.CharField(max_length=200, null= False)
    category = models.CharField(max_length=200, null= False)
    type = models.CharField(max_length=200, blank=True,  null=False)
    stay_type = models.CharField(max_length=200, blank=True, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promot_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank= True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    location = models.CharField(max_length=200, null= True)
    bedroom = models.IntegerField(default=1, blank=False)
    guest_number= models.IntegerField(default=0, blank=True, null= True)
    bathroom = models.IntegerField(default=1, blank=False)
    amenities = models.ManyToManyField(Amenities, blank=True)
    description = models.TextField(null=False)
    images = models.ImageField(upload_to= "products/", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Room.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return str(self.uuid) or self.slug
class Orders(models.Model):

    order_number = models.CharField(max_length=30, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE, related_name='orders')
    reference = models.CharField(max_length=100, blank=True, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100, blank=True, default='cast')
    payment_status = models.CharField(max_length=100, default="unpaid")
    delevery_method = models.CharField(max_length=100, blank=True, null=True)
    order_status = models.CharField(max_length=100, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *arg, **kwargs):
        if not self.order_number:
            year = now().year
            last_order = Orders.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id + 1
            else:
                last_id = 1
            self.order_number = f"ORD-{year}-{last_id:04d}"
            self.reference = f"REF-{year}-{last_id:04d} "
        super().save(*arg, **kwargs)
        
    def __str__(self):
        return self.order_number or self.room
class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='orderitems')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='orderitems')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # room.price * quantity
    
    def __str__(self):
        return self.order or self.room