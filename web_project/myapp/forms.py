from django import forms
from django.forms import ModelForm
from .models import Profile, Product, Notification
from messenger.models import Message
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['city', 'address', 'name', 'surname', 'profile_picture']
     
    city = forms.CharField(required=False)
    address = forms.CharField(required=False)
    name = forms.CharField(required=False)
    surname = forms.CharField(required=False)

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'brand', 'quantity', 'image', 'status']
        labels = {
            'title': 'Naziv proizvoda',
            'description': 'Opis proizvoda',
            'price': 'Cijena (EUR)',
            'category': 'Kategorija',
            'brand': 'Brend', 
            'quantity': 'Količina',
            'image': 'Slika proizvoda',
            'status': 'Status',
        }
        widgets = {
            'status': forms.Select(choices=[('Dostupno', 'Dostupno'), ('Nedostupno', 'Nedostpuno')]),
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'placeholder': 'Unesite naziv proizvoda'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Unesite cijenu u EUR'}),
            'category': forms.Select(attrs={'placeholder': 'Odaberite kategoriju'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Unesite robnu marku proizvoda'}), 
            'quantity': forms.NumberInput(attrs={'placeholder': 'Unesite količinu'}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class MessageForm(forms.ModelForm):
    receiver_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    
    class Meta:
        model = Message
        fields = ['text']
    
    def __init__(self, *args, **kwargs):
        receiver_id = kwargs.pop('receiver_id', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        if receiver_id is not None:
            self.fields['receiver_id'].initial = receiver_id

class MessageForm2(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text'] 

    def __init__(self, *args, **kwargs):
        self.receiver = kwargs.pop('receiver', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.receiver is None:
            raise forms.ValidationError("Receiver is required.")
        return cleaned_data