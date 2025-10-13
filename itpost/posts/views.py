from django.shortcuts import render, redirect
from django.views import View

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.db.models import Q, OuterRef, Subquery, Exists
from django.core.paginator import Paginator


from .models import *
from .forms import *


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
            return redirect('prof_manage_course_view')
        elif user.groups.filter(name="Student").exists():
            return redirect('student_view')
        else:
            return redirect('admin_view')
        

class StudentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.view_post'
    def get(self, request):
        user = request.user
        context = get_user_context(user)
        request.session['return_to'] = request.path
        posts = Post.objects.filter(
                course__isnull=True,
                status = 'approved'
                ).order_by('-created_at')
        
        if user.groups.filter(name="Student").exists():
            info = user.academic_info

            visibility_filter = Q(years=info.year) & Q(majors=info.major)

            if info.specialization:
                visibility_filter &= (
                    Q(specializations=info.specialization) |
                    Q(specializations__isnull=True)
                )
            else:
                visibility_filter &= Q(specializations__isnull=True)

            posts = posts.filter(
                visibility_filter | Q(created_by=user)
            ).distinct().order_by('-created_at')

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
    

class StudentCreatePostView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.add_post'
    def get(self, request):
        context = get_user_context(request.user)
        form = StudentPostForm()
        context['form'] = form
        return render(request, 'student_create_post.html', context)
    
    def post(self, request):
        form = StudentPostForm(request.POST, request.FILES)
        user = request.user
        
        if form.is_valid():
            
            post = form.save(commit=False)
            post.created_by = request.user
            if user.groups.filter(name="Professor").exists():
                post.status = 'approved'
            post.save()
            form.save_m2m()

            if post.years.count() == 0 :
                for i in YearOption.objects.all():
                    post.years.add(i)
            if post.majors.count() == 0:
                for i in Major.objects.all():
                    post.majors.add(i)

            for f in request.FILES.getlist('files'):
                PostFile.objects.create(post=post, file=f)

            return redirect('student_view')
        
        context = get_user_context(user)
        print(form.errors)
        context['form'] = form
        return render(request, 'student_create_post.html', context)
    
class EditPostView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_post'
    def get(self, request, post_id):
        user = request.user
        context = get_user_context(user)
        post = Post.objects.get(pk=post_id)
        
        if post.course:
            form = ProfessorPostForm(instance=post)
        else:
            form = StudentPostForm(instance=post)

        context['form'] = form
        context['post'] = post
        return render(request, 'edit_post.html', context)

    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        if post.course:
            form = ProfessorPostForm(request.POST, request.FILES, instance=post, is_edit=True)
        else:
            form = StudentPostForm(request.POST, request.FILES, instance=post, is_edit=True)
        
        if form.is_valid():
            post = form.save(commit=False)
            if request.user.groups.filter(name="Student").exists():
                post.status = 'pending'
            post.save()
            form.save_m2m()
          
            if request.FILES.getlist('files'):
                post.files.all().delete()
                for f in request.FILES.getlist('files'):
                    PostFile.objects.create(post=post, file=f)

            if request.user.groups.filter(name="Admin").exists():
                return redirect('admin_post_view')
            elif post.course:
                return redirect('course_detail', post.course.course_code)
            else:
                return redirect('student_view')
        
        print(form.errors)
        context = {}
        context['form'] = form
        context['post'] = post
        return render(request, 'edit_post.html', context)
        
class StudentCourseView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.view_course'
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
    

class ProfManageCourseView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.add_course'

    def get(self, request):
        request.session['return_to'] = request.path
        context = get_user_context(request.user)

        latest_post = Post.objects.filter(course=OuterRef('pk')).order_by('-created_at')

        course_lists = Course.objects.filter(
            created_by=request.user
        ).annotate(
            latest_post_title=Subquery(latest_post.values('title')[:1]),
            latest_post_created=Subquery(latest_post.values('created_at')[:1])
        ).distinct().order_by('-created_at')

        course_form = CourseForm()

        colors1 = ['blue', 'emerald', 'orange']

        for i, course in enumerate(course_lists):
            course.color = colors1[i % len(colors1)]

        context['course_form'] = course_form
        context['course_lists'] = course_lists

        context['year_choices'] = YearOption.objects.all()
        context['major_choices'] = Major.objects.all()
        context['specialization_choices'] = Specialization.objects.all()

        return render(request, 'prof_manage_course.html', context)

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
                return redirect('back')
            
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


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = request.user
        context = get_user_context(user)
        request.session['return_to'] = request.path

        try:
            users = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('/')
        
        post_counts = {
            'approved': Post.objects.filter(created_by=users, status=Post.PostStatus.APPROVED).count(),
            'pending': Post.objects.filter(created_by=users, status=Post.PostStatus.PENDING).count(),
            'rejected': Post.objects.filter(created_by=users, status=Post.PostStatus.REJECTED).count(),
        }
        liked_posts = Post.objects.filter(liked_by=users).order_by('-created_at')
        context['post_counts'] = post_counts
        context['liked_posts'] = liked_posts

        if users.groups.filter(name="Student").exists():
            courses = Course.objects.filter(enrollments__student=users, enrollments__is_approved=True)

            posts = Post.objects.filter(
                course__isnull=True,
                status=Post.PostStatus.APPROVED,
                created_by=users
            ).order_by('-created_at')

            if user.groups.filter(name="Student").exists() and not user == users:
                info = user.academic_info

                posts = posts.filter(
                    years=info.year,
                    majors=info.major
                )

                if info.specialization:
                    posts = posts.filter(
                        Q(specializations=info.specialization) |
                        Q(specializations__isnull=True)
                    )
                else:
                    posts = posts.filter(specializations__isnull=True)

            context['posts'] = posts


        elif users.groups.filter(name="Professor").exists():
            courses = Course.objects.filter(created_by=users)

            if user == users or user.is_staff:
                posts = Post.objects.filter(created_by=users).order_by('-created_at')
                context['posts'] = posts

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
    permission_required = 'auth.add_user'
    
    def get(self, request):
        form = CustomUserCreationForm()
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

        context['form'] = form
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

class AdminPostView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'posts.change_group'

    def get(self, request):
        context = get_all_info_context(request.user)

        pending_posts_list = Post.objects.prefetch_related('files').filter(status='pending').order_by('-created_at')

        paginator = Paginator(pending_posts_list, 2)
        page_number = request.GET.get('page')
        pending_posts = paginator.get_page(page_number)

        search_query = request.GET.get("search", "").strip()
        filter = request.GET.get('status')

        posts = Post.objects.all().order_by('-created_at')

        if filter:
            posts = posts.filter(status=filter)

        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(created_by__username__icontains=search_query)
            )
        
        context['posts'] = posts
        context['pending_posts'] = pending_posts
        return render(request, 'admin_manage_post.html', context)
