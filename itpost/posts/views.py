from django.shortcuts import render, redirect
from django.views import View

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group

from .models import *
from .forms import *

def get_user_context(user):
    group = user.groups.first()
    return {
        'user': user,
        'group': group,
    }


class MainView(LoginRequiredMixin, View):
    def get(self, request):
        context = get_user_context(request.user)
        return render(request, 'base.html', context)
    

class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, 'login_page.html', {'form': form})
    
    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')


        return render(request,'login_page.html', {"form":form})
    
def logout_view(request):
    logout(request)
    return redirect('login_view')

def test_view(request):
    return render(request, 'test.html')

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        academic_form = AcademicInfoForm()

        context = {
            'form': form,
            'academic_form': academic_form
        }
        return render(request, 'register_page.html', context)
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        academic_form = AcademicInfoForm(request.POST)
        if form.is_valid() and academic_form.is_valid():
            user = form.save()

            student_group = Group.objects.get(name='Student')
            user.groups.add(student_group)

            academic = academic_form.save(commit=False)
            academic.user = user
            academic.save()

            return redirect('login_view')
        else:
            print(form.errors)
            print(academic_form.errors)


        
        context = {
            'form': form,
            'academic_form': academic_form
        }
        return render(request, 'register_page.html', context)
