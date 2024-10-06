from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """
    create_user has ValueError if user didn't insert Email and username
    we normalize the email so its easier to authenticate (removing whitespace , lower casing the emails)
    using set_password to hash the password for more secure reason before saving it
    then saving it using self._db to ensure if i have multiple databases it saves the user to the databases connected to
    UserManager
    """
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')

        user = self.model(email=self.normalize_email(email), username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    """
    Creating superuser with setdefault is_staff and is_superuser to True
    and validating it by raising errors if its not True
    then creating the user
    calling create_user to create the superuser to handle creation and password hashing
    """
    def create_superuser(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        if not username:
            raise ValueError('username is Required')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be staff')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be superuser')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """
    Extending AbstractUser and adding email and username to be Unqiue
    bio and profilePicture to be optional
    changing username field to Email so users loggin using email instead of username
    and making username required upon registration

    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=250, unique=True)
    bio = models.TextField(max_length=250, blank=True, null=True, default='No bio provided')
    profile_picture = models.ImageField(blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

