from django.shortcuts import render, redirect
from django.views import View

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.db.models import Q, OuterRef, Subquery, Exists


from .models import *
from .forms import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def get_user_context(user):
    group = user.groups.first()
    return {
        'user': user,
        'group': group,
    }

def back(request):
    return redirect(request.session.get('return_to', '/'))

class MainView(LoginRequiredMixin, View):
    def get(self, request):
        context = get_user_context(request.user)
        user = request.user

        if user.groups.filter(name="Professor").exists():
            return redirect('manage_course_view')
        elif user.groups.filter(name="Student").exists():
            return redirect('student_view')
        else:
            return render(request, 'base.html', context)
        

class StudentView(LoginRequiredMixin, View):
    def get(self, request):
        context = get_user_context(request.user)
        user = request.user

        posts = Post.objects.all()

        filter = request.GET.get('filter')
        if filter:
            posts = posts.filter(post_type__id=filter)

        enrolled_courses = Course.objects.filter(
            enrollments__student=request.user,
            enrollments__is_approved=True
        ).distinct()
        context['enrolled_courses'] = enrolled_courses
        context['posts'] = posts
        return render(request, 'student_home.html', context)
    

class StudentCreatePostView(LoginRequiredMixin, View):
    def get(self, request):
        context = get_user_context(request.user)
        form = StudentPostForm()
        context['form'] = form
        return render(request, 'student_create_post.html', context)

        
class StudentCourseView(LoginRequiredMixin, View):
    def get(self, request):
        context = get_user_context(request.user)
        request.session['return_to'] = request.path
        user = request.user
        user_year = user.academic_info.year
        user_majors = user.academic_info.major
        user_specializations = user.academic_info.specialization

        colors1 = ['purple', 'pink', 'rose']
        colors2 = ['blue', 'emerald', 'orange']


        enrolled_ids = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)

        available_courses = Course.objects.exclude(id__in=enrolled_ids).filter(
            Q(allowed_years__isnull=True) | Q(allowed_years=user_year),
            Q(allowed_majors__isnull=True) | Q(allowed_majors=user_majors),
            Q(allowed_specializations__isnull=True) | Q(allowed_specializations=user_specializations)
        ).distinct().order_by('created_at')

        approved_enrollment = Enrollment.objects.filter(
            course=OuterRef('pk'),
            student=request.user,
            is_approved=True
        )

        latest_post = Post.objects.filter(course=OuterRef('pk')).order_by('-created_at')

        enrolled_courses = Course.objects.filter(
            enrollments__student=request.user
        ).annotate(
            is_approved=Exists(approved_enrollment),
            latest_post_title=Subquery(latest_post.values('title')[:1]),
            latest_post_created=Subquery(latest_post.values('created_at')[:1])
        ).distinct().order_by('-is_approved')


        for i, course in enumerate(available_courses):
            course.color = colors1[i % len(colors1)]
        for i, course in enumerate(enrolled_courses):
            course.color = colors2[i % len(colors2)]

        context['available_courses'] = available_courses
        context['enrolled_courses'] = enrolled_courses
        return render(request, 'student_course.html', context)
        

class ManageCourseView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.add_course'

    def get(self, request):
        request.session['return_to'] = request.path
        context = get_user_context(request.user)
        course_lists = Course.objects.filter(created_by=request.user)

        course_form = CourseForm()

        context['course_form'] = course_form
        context['course_lists'] = course_lists

        return render(request, 'professor_page.html', context)
    
    def post(self, request):
        context = get_user_context(request.user)
        course_form = CourseForm(request.POST)

        if course_form.is_valid():
            course = course_form.save(commit=False)
            course.created_by = request.user
            course.save()
            course_form.save_m2m()
            return redirect('manage_course_view')
        
        course_lists = Course.objects.filter(created_by=request.user)
        context['course_form'] = course_form
        context['course_lists'] = course_lists

        return render(request, 'professor_page.html', context)

class EditCourseView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_course'

    def get(self, request, course_id):
        user = request.user
        context = get_user_context(request.user)
        course = Course.objects.get(pk=course_id)

        if course.created_by == user:
            course_form = CourseForm(instance=course)
            context['course_form'] = course_form
            context['course_id'] = course_id
            return render(request, 'edit_course.html', context)
        
        return redirect('back')
    
    def post(self, request, course_id):
        user = request.user
        context = get_user_context(request.user)
        course = Course.objects.get(pk=course_id)
        course_form = CourseForm(request.POST, instance=course)

        if course.created_by == user:
            if course_form.is_valid():
                course_form.save()
                return redirect('manage_course_view')
            
            context['course_form'] = course_form
            context['course_id'] = course_id
            return render(request, 'edit_course.html', context)
        
        return redirect('/')
    

class ProfCreatePostView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.add_course'

    def get(self, request):
        context = get_user_context(request.user)
        form = ProfessorPostForm(user=request.user)

        context['form'] = form
        return render(request, 'prof_create_post.html', context)
    
    def post(self, request):
        form = ProfessorPostForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user

            post.status = 'approved'
            post.save()
            form.save_m2m()

            course = form.cleaned_data['course']
            course_code = course.course_code

            for f in request.FILES.getlist('files'):
                PostFile.objects.create(post=post, file=f)

            return redirect('course_detail', course_code=course_code)
        
        context = get_user_context(request.user)
        context['form'] = form
        return render(request, 'prof_create_post.html', context)
    

class CourseDetailView(LoginRequiredMixin, View):
    def get(self, request, course_code):
        user = request.user
        context = get_user_context(request.user)

        course = Course.objects.get(course_code=course_code)

        if user.groups.filter(name="Student").exists():
            if not course.enrollments.filter(student=user, is_approved=True).exists():
                return redirect('/')


        posts = course.posts.filter(status='approved')

        filter = request.GET.get('filter')
        if filter:
            posts = posts.filter(post_type__id=filter)

        context['course'] = course
        context['posts'] = posts


        return render(request, 'course_detail.html', context)
    

class CourseDetailStudentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_course'

    def get(self, request, course_code):
        user = request.user
        context = get_user_context(request.user)

        course = Course.objects.get(course_code=course_code)

        if user == course.created_by:
            enrollments = Enrollment.objects.filter(course=course)
            # students = User.objects.filter(enrollments__course=course).distinct()
            # context['students'] = students
            context['course'] = course
            context['enrollments'] = enrollments

            return render(request, 'course_detail_student.html', context)
        
        return redirect('manage_course_view')



class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, 'login_page.html', {'form': form})
    
    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            login(request, form.get_user())
            return redirect(next_url)


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



class EnrollCourseAPIView(APIView):
    def post(self, request, course_id):
        user = request.user

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        existing = Enrollment.objects.filter(student=user, course=course).first()
        if existing:
            return Response({'success': False, 'message': 'Already Enrolled'}, status=status.HTTP_200_OK)

        enroll = Enrollment.objects.create(student=user, course=course)

        return Response({'success': True, 'message': 'Enrollment request sent', 'enrollment_id': enroll.id}, status=status.HTTP_201_CREATED)
    
    def put(self, request, course_id):

        try:
            enrollments = Enrollment.objects.get(pk=course_id)
        except Enrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollments.is_approved = True
        enrollments.save()

        return Response({'success': True, 'message': 'Enrollment approve sent'}, status=status.HTTP_200_OK)

