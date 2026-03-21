from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Room

class RegisterFrom(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password1',
            'password2'
        )
        
class ProductForm(forms.ModelForm):
    CATEGORY_CHOICES = [
    ('guesthouse', 'Guesthouse'),
    ('serviced apartment', 'Serviced Apartment'),
    ('hotel', 'hotel'),
    ('resort', 'Resort'),
    ('hostel', 'Hostel'),
]
    TYPE_CHOICES = [
        ('single room', "Single Room"),
        ('double room', 'Double Room'),
        ('twin room', "Twin Room"),
        ('triple room', "Triple Room"),
        ('family room', "Family Room"),
        ('suite', "Suite")
    ]
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select input'})
    )
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select input'})
    )
    class Meta:
        model = Room
        fields = (
            'title', 
            'category',
            'type',
            'stay_type',
            'price', 
            'location',
            'bedroom',
            'bathroom',
            'guest_number',
            'amenities',
            'description', 
            'images'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control input'}),
            'category': forms.Select(attrs={'class': 'form-select input'}),
            'type': forms.Select(attrs={'class': 'form-select input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control input'}),
            'location': forms.TextInput(attrs={'class': 'form-control input'}),
            'bedroom': forms.NumberInput(attrs={'class': 'form-control input'}),
            'bathroom': forms.NumberInput(attrs={'class': 'form-control input'}),
            'guest_number': forms.NumberInput(attrs={'class': 'form-control input'}),
            'amenities': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'class': 'form-control text-area'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control input'}),
        }