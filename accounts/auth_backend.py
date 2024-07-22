from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connection
from werkzeug.security import check_password_hash

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, password FROM users WHERE username = %s", [username])
            user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            try:
                django_user = User.objects.get(username=username)
            except User.DoesNotExist:
                django_user = User(username=username)
                django_user.save()
            return django_user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
