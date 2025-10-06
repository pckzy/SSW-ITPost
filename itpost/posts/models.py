from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='profile/', blank=True, null=True, default="profile/no-profile.png")

    def __str__(self):
        return f"{self.user.username}'s profile"

class Major(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100,)

    def __str__(self):
        return f"{self.code}"


class Specialization(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='specializations')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"
    

class YearOption(models.Model):
    year = models.PositiveIntegerField(choices=[(i, f'ปี {i}') for i in range(1, 5)], unique=True)

    def __str__(self):
        return f"ปี {self.year}"


class AcademicInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_info')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveIntegerField(choices=[(i, f'ปี {i}') for i in range(1, 5)])

    def __str__(self):
        spec = self.specialization.name if self.specialization else "ไม่มีแขนง"
        return f"{self.user.username} - {self.major.name} - {spec} (Year {self.year})"


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created')
    created_at = models.DateTimeField(auto_now_add=True)

    allowed_years = models.ManyToManyField(YearOption, blank=True, related_name='courses_by_year')
    allowed_majors = models.ManyToManyField(Major, blank=True, related_name='courses_by_major')
    allowed_specializations = models.ManyToManyField(Specialization, blank=True, related_name='courses_by_spec')

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    def student_count(self):
        return self.enrollments.filter(is_approved=True).count()

    def post_count(self):
        return self.posts.filter(status='approved').count()


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    is_approved = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)


class PostType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    for_course = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Post(models.Model):
    class PostStatus(models.TextChoices):
        PENDING = 'pending', 'รออนุมัติ'
        APPROVED = 'approved', 'อนุมัติแล้ว'
        REJECTED = 'rejected', 'ปฏิเสธ'

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    post_type = models.ForeignKey(PostType, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')

    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    years = models.ManyToManyField(YearOption, blank=True)
    majors = models.ManyToManyField(Major, blank=True)
    specializations = models.ManyToManyField(Specialization, blank=True)

    annonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=PostStatus.choices, default=PostStatus.PENDING)

    def __str__(self):
        return self.title
    
    def like_count(self):
            return self.liked_by.count()
    
    def clean(self):
        if self.course and not self.post_type.for_course:
            raise ValidationError("โพสต์ในคอร์สต้องใช้ประเภทที่ for_course=True")
        if not self.course and self.post_type.for_course:
            raise ValidationError("โพสต์ทั่วไปต้องใช้ประเภทที่ for_course=False")

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content}"

class PostFile(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name