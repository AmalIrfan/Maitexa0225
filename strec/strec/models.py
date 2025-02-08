# models.py
from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Create a relationship with the User model
    datafile = models.FileField(upload_to='user_data_files/')  # Field to store the uploaded file

    def __str__(self):
        return f"Data for {self.user.username}"