from django.shortcuts import render, redirect
from django.views import View

from .models import *
from .forms import *

class MainView(View):
    def get(self, request):
        return render(request, 'base.html')