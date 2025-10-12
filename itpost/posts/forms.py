from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
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


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'description', 'allowed_years', 'allowed_majors', 'allowed_specializations',
        ]
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder':'เช่น CS101'}),
            'course_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder':'เช่น Computer Programming'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder':'รายละเอียดเกี่ยวกับรายวิชา...'}),
            'allowed_years': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'size': '5'}),
            'allowed_majors': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'size': '5'}),
            'allowed_specializations': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'size': '5'})
        }

    def clean_course_code(self):
        code = self.cleaned_data.get('course_code')
        qs = Course.objects.filter(course_code__iexact=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("รหัสวิชานี้มีอยู่แล้วในระบบ")

        return code


class ProfessorPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'post_type', 'course'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'post_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'title': forms.TextInput(attrs={'placeholder':'เช่น ประกาศงดสอน', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder':'รายละเอียดประกาศ...', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        self.fields['course'].required = True
        self.fields['course'].empty_label = "-- เลือกคอร์สเรียน --"
        self.fields['post_type'].empty_label = "-- เลือกชนิดของประกาศ --"
        self.fields['post_type'].queryset = PostType.objects.filter(for_course=True)

        if user:
            self.fields['course'].queryset = Course.objects.filter(created_by=user)
        
        if is_edit:
            # ทำให้ post_type และ course ไม่สามารถแก้ไขได้
            self.fields['post_type'].disabled = True
            self.fields['course'].disabled = True


class StudentPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'post_type', 'years', 'majors', 'specializations', 'annonymous'
        ]
        widgets = {
            'post_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'title': forms.TextInput(attrs={'placeholder':'เช่น หาสมาชิกเข้ากลุ่มโปรเจค', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder':'รายละเอียดประกาศ...', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'years': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'size': '5'}),
            'majors': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'size': '5'}),
            'specializations': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'size': '5'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['post_type'].empty_label = "-- เลือกชนิดของประกาศ --"
        self.fields['post_type'].queryset = PostType.objects.filter(for_course=False)
        if self.instance and self.instance.pk:
            self.fields['post_type'].disabled = True


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].required = False
        self.fields['new_password1'].required = False
        self.fields['new_password2'].required = False
        self.fields['old_password'].widget.attrs.update({
            'autofocus': False,
            'placeholder': '********',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        })
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': '********',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': '********',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        })

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email'
        ]
        widgets = {
            "username": forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            "first_name": forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            "last_name": forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            "email": forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
    
        if email and not email.endswith('@kmitl.ac.th'):
            raise forms.ValidationError("อีเมลสถาบันเท่านั้น")
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username__iexact=username)
        pattern = r'^[0-9]{2}07[0-9]{4}$'
        
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("ชื่อผู้ใช้นี้มีอยู่แล้วในระบบ")

        if not self.instance.groups.filter(name="Professor").exists():
            if not re.match(pattern, username):
                raise forms.ValidationError('รหัสนักศึกษาเท่านั้น')

        return username

class AcademicUpdateForm(forms.ModelForm):
    class Meta:
        model = AcademicInfo
        fields = [
            'major', 'specialization', 'year'
        ]
        widgets = {
            'year': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-600'}),
            'major': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-600'}),
            'specialization': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-600'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['major'].empty_label = "-- เลือกสาขา --"
        self.fields['specialization'].empty_label = "-- เลือกแขนง --"

        if user and user.groups.filter(name="Student").exists():
            for field in ['major', 'specialization', 'year']:
                self.fields[field].widget.attrs.update({
                    'readonly': True,
                    'class': self.fields[field].widget.attrs.get('class', '') + ' cursor-not-allowed'
                })

    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'hidden'})
        }

