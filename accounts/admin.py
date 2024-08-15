from django.contrib import admin
from .models import Relation, Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class ExetingProfileUser(UserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, ExetingProfileUser)
admin.site.register(Relation)
admin.site.register(Profile)