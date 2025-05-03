import bleach
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Book, User


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price']

    def clean_title(self):
        title = self.cleaned_data['title']
        return bleach.clean(title)

    def clean_author(self):
        author = self.cleaned_data['author']
        return bleach.clean(author)


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label='Роль')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        cleaned_email = bleach.clean(email)
        if User.objects.filter(email=cleaned_email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован.')
        return cleaned_email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        cleaned_username = bleach.clean(username)
        if User.objects.filter(username=cleaned_username).exists():
            raise forms.ValidationError('Этот логин уже занят.')
        return cleaned_username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать не менее 8 символов.')
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError('Пароль должен содержать буквы и цифры.')
        return password


class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text='Оставьте пустым, если не хотите менять пароль.',
        label='Пароль'
    )
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label='Роль')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'role']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'first_name': 'Имя',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        cleaned_username = bleach.clean(username)
        if User.objects.exclude(pk=self.instance.pk).filter(username=cleaned_username).exists():
            raise forms.ValidationError('Этот логин уже занят.')
        return cleaned_username

    def clean_email(self):
        email = self.cleaned_data['email']
        cleaned_email = bleach.clean(email)
        if User.objects.exclude(pk=self.instance.pk).filter(email=cleaned_email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован.')
        return cleaned_email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return bleach.clean(username)