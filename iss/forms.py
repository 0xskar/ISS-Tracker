from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, City, Country


class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = ['email', 'name', 'country', 'city', 'password']


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=200)
    name = forms.CharField(max_length=200)
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)
    city = forms.ModelChoiceField(queryset=City.objects.none(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'name', 'country', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user,
                                        email=user.email,
                                        name=self.cleaned_data['name'],
                                        country=self.cleaned_data['country'],
                                        city=self.cleaned_data['city'],
                                        password=user.password)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})