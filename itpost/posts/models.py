from django.db import models
from django.contrib.auth.models import User


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


class AcademicInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_info')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveIntegerField(choices=[(i, f'ปี {i}') for i in range(1, 5)])

    def __str__(self):
        spec = self.specialization.name if self.specialization else "ไม่มีแขนง"
        return f"{self.user.username} - {self.major.name} - {spec} (Year {self.year})"
