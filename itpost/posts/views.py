from django.shortcuts import render, redirect
from django.views import View

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.db.models import Q, OuterRef, Subquery, Exists
from django.core.paginator import Paginator


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
            return redirect('admin_view')
        

class StudentView(LoginRequiredMixin, View):
    def get(self, request):
        context = get_user_context(request.user)
        request.session['return_to'] = request.path
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
        course_lists = Course.objects.filter(created_by=request.user).order_by('-created_at')

        course_form = CourseForm()

        context['course_form'] = course_form
        context['course_lists'] = course_lists

        context['year_choices'] = YearOption.objects.all()
        context['major_choices'] = Major.objects.all()
        context['specialization_choices'] = Specialization.objects.all()

        return render(request, 'professor_page.html', context)

class EditCourseView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_course'

    def get(self, request, course_id):
        user = request.user
        context = get_user_context(request.user)
        course = Course.objects.get(pk=course_id)

        if course.created_by == user or user.is_staff:
            course_form = CourseForm(instance=course)
            context['course_form'] = course_form
            context['course'] = course
            return render(request, 'edit_course.html', context)
        
        return redirect('back')
    
    def post(self, request, course_id):
        user = request.user
        context = get_user_context(request.user)
        course = Course.objects.get(pk=course_id)
        course_form = CourseForm(request.POST, instance=course)

        if course.created_by == user or user.is_staff:
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


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        context = get_user_context(request.user)
        request.session['return_to'] = request.path

        try:
            users = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('/')

        if users.groups.filter(name="Student").exists():
            courses = Course.objects.filter(enrollments__student=users, enrollments__is_approved=True)
        elif users.groups.filter(name="Professor").exists():
            courses = Course.objects.filter(created_by=users)
        else:
            return redirect('/')
        
        context['courses'] = courses
        context['users'] = users

        return render(request, 'user_profile.html', context)
    

class EditProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        context = get_user_context(request.user)

        try:
            users = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('/')
        
        if request.user.is_staff or users == request.user:

            profile, _ = Profile.objects.get_or_create(user=users)
            profile_form = ProfileUpdateForm(instance=profile)
            
            password_form = CustomPasswordChangeForm(user=users)
            user_form = UserUpdateForm(instance=users)

            if users.groups.filter(name="Student").exists():
                academic_form = AcademicUpdateForm(instance=users.academic_info, user=request.user)
                context['academic_form'] = academic_form
            
            context['users'] = users
            context['password_form'] = password_form
            context['user_form'] = user_form
            context['profile_form'] = profile_form

            return render(request, 'edit_profile.html', context)
        else:
            return redirect('/')
        
    def post(self, request, username):
        context = get_user_context(request.user)

        try:
            users = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('/')
        
        if request.user.is_staff or users == request.user:
            profile = Profile.objects.get(user=users)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            user_form = UserUpdateForm(request.POST, instance=users)
            password_form = CustomPasswordChangeForm(user=users, data=request.POST)
            academic_form = None

            if users.groups.filter(name="Student").exists():
                academic_form = AcademicUpdateForm(request.POST, instance=users.academic_info, user=request.user)
                context['academic_form'] = academic_form

            valid_user = user_form.is_valid()
            valid_profile = profile_form.is_valid()
            valid_academic = academic_form.is_valid() if academic_form else True

            if request.POST.get('old_password') or request.POST.get('new_password1') or request.POST.get('new_password2'):
                if password_form.is_valid():
                    password_form.save()
                    update_session_auth_hash(request, users)
                else:
                    valid_user = valid_profile = valid_academic = False

            if valid_user and valid_profile and valid_academic:
                
                user_form.save()
                profile_form.save()
                if academic_form:
                    academic_form.save()
                
                return redirect('profile_view', username=users.username)
            
            context['users'] = users
            context['password_form'] = password_form
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return render(request, 'edit_profile.html', context)

        else:
            return redirect('/')
        

def get_all_info_context(user):
    user_count = User.objects.all().count()
    course_count = Course.objects.all().count()
    post_count = Post.objects.all().count()
    post_request_count = Post.objects.filter(status='pending').count()
    group = user.groups.first()

    return {
        'user': user,
        'group': group,
        'user_count': user_count,
        'course_count': course_count,
        'post_count': post_count,
        'post_request_count': post_request_count,
    }


class AdminView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_group'
    
    def get(self, request):
        context = get_all_info_context(request.user)

        search_query = request.GET.get("search", "").strip()
        group_query = request.GET.get("group", "")

        request.session['return_to'] = request.path

        users = User.objects.all().order_by('username')
        context['user_count'] = users.count()

        if group_query:
            users = users.filter(groups__id=group_query)

        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

        all_groups = Group.objects.all()

        context['users'] = users
        context['all_groups'] = all_groups
        return render(request, 'admin_dashboard.html', context)
    


class AdminCourseView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_group'

    def get(self, request):
        context = get_all_info_context(request.user)

        search_query = request.GET.get("search", "").strip()

        request.session['return_to'] = request.path

        course_lists = Course.objects.all().order_by('-created_at')

        if search_query:
            course_lists = course_lists.filter(
                Q(course_code__icontains=search_query) |
                Q(course_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        paginator = Paginator(course_lists, 3)
        page_number = request.GET.get('page')
        courses = paginator.get_page(page_number)
        

        context['course_lists'] = courses
        return render(request, 'admin_manage_course.html', context)
