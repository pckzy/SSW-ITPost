from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import *
import re


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'placeholder': 'กรอกชื่อผู้ใช้งาน',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'กรอกรหัสผ่าน',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', "password1", "password2"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                'placeholder': 'กรอกชื่อจริง',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'autofocus': True
            }),
            "last_name": forms.TextInput(attrs={
                'placeholder': 'กรอกนามสกุล',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            "email": forms.EmailInput(attrs={
                'placeholder': 'กรอกอีเมล',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['username'].widget.attrs.update({
            'autofocus': False,
            'placeholder': 'กรอกชื่อผู้ใช้งาน',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'กรอกรหัสผ่าน',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'ยืนยันรหัสผ่าน',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email and not email.endswith('@kmitl.ac.th'):
            raise forms.ValidationError("อีเมลสถาบันเท่านั้น")

        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        pattern = r'^[0-9]{2}07[0-9]{4}$'

        if not re.match(pattern, username):
            raise forms.ValidationError('รหัสนักศึกษาเท่านั้น')

        return username


class AcademicInfoForm(forms.ModelForm):
    class Meta:
        model = AcademicInfo
        fields = [
            'major', 'specialization', 'year'
        ]
        widgets = {
            'year': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'major': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'specialization': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['major'].empty_label = "-- เลือกสาขา --"
        self.fields['specialization'].empty_label = "-- เลือกแขนง --"