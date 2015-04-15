from planner.forms import YearForm, UserChangeForm, UserCreationForm
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from planner.models import *
from django.conf.urls import patterns, url
from planner.views import YearFormView



class EmailUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'team')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'team')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # 'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
            'fields': ('email', 'first_name', 'last_name', 'team')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email', 'first_name', 'last_name',)
    filter_horizontal = ()

class HolidayAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(HolidayAdmin, self).get_urls()
        my_urls = patterns('', url(r'^add_weekend/$', YearFormView.as_view(), name='planner_holiday_add_weekend')
        )
        return my_urls + urls

    change_list_template = 'planner/change_list.html'



# Now register the new UserAdmin...
admin.site.register(EmailUser, EmailUserAdmin)
admin.site.register(Absence)
admin.site.register(Team)
admin.site.register(AbsenceRange)
admin.site.register(Holiday, HolidayAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)