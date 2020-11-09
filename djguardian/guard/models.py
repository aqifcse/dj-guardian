import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import AbstractUser
from guardian.models import UserObjectPermissionAbstract, GroupObjectPermissionAbstract


class BigUserObjectPermission(UserObjectPermissionAbstract):
   id = models.BigAutoField(editable=False, unique=True, primary_key=True)
   class Meta(UserObjectPermissionAbstract.Meta):
      abstract = False
      indexes = [
         *UserObjectPermissionAbstract.Meta.indexes,
         models.Index(fields=['content_type', 'object_pk', 'user']),
      ]

class BigGroupObjectPermission(GroupObjectPermissionAbstract):
   id = models.BigAutoField(editable=False, unique=True, primary_key=True)
   class Meta(GroupObjectPermissionAbstract.Meta):
      abstract = False
      indexes = [
         *GroupObjectPermissionAbstract.Meta.indexes,
         models.Index(fields=['content_type', 'object_pk', 'group']),
      ]

class Post(models.Model):
    title = models.CharField('title', max_length=64)
    slug = models.SlugField(max_length=64)
    content = models.TextField('content')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        permissions = (
            ('hide_post', 'Can hide post'),
        )
        get_latest_by = 'created_at'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return {'post_slug': self.slug}

class Task(models.Model):
    summary = models.CharField(max_length=32)
    content = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('assign_task', 'Assign task'),
        )

# class CustomUser(AbstractUser):
#     real_username = models.CharField(max_length=120, unique=True)
#     birth_date = models.DateField()  # field without default value

#     USERNAME_FIELD = 'real_username'

# def get_anonymous_user_instance(AbstractUser):
#     return User(real_username='Anonymous', birth_date=datetime.date(1970, 1, 1))

@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    """
    Create a Profile instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save.
    """
    user, created = kwargs["instance"], kwargs["created"]
    if created and user.username != settings.ANONYMOUS_USER_NAME:
        from profiles.models import Profile
        profile = Profile.objects.create(pk=user.pk, user=user, creator=user)
        assign_perm("change_user", user, user)
        assign_perm("change_profile", user, profile)


