from planner.forms import UserChangeForm, UserCreationForm
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
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'team', 'is_teamleader')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'team', 'is_teamleader')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # 'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}
            'fields': ('email', 'first_name', 'last_name', 'team', 'is_teamleader')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name', 'team')
    ordering = ('email', 'first_name', 'last_name', 'team')
    filter_horizontal = ()


class HolidayAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(HolidayAdmin, self).get_urls()
        my_urls = patterns('', url(r'^add_weekend/$', YearFormView.as_view(), name='planner_holiday_add_weekend')
        )
        return my_urls + urls

    change_list_template = 'planner/change_list.html'


class EmailUserInline(admin.TabularInline):
    model = EmailUser
    fields = ['email', 'first_name', 'last_name', 'is_teamleader']
    template = 'admin/tabular.html'
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [EmailUserInline]

    def member_count(self, obj):
        return obj.emailuser_set.count()

    def has_teamleader(self, obj):
        teamleaders = obj.emailuser_set.filter(is_teamleader=True)
        return teamleaders.exists()
    has_teamleader.boolean = True

    list_display = ('name', 'member_count', 'has_teamleader')


# Now register the new UserAdmin...
admin.site.register(EmailUser, EmailUserAdmin)
admin.site.register(Absence)
admin.site.register(Team, TeamAdmin)
admin.site.register(AbsenceRange)
admin.site.register(Holiday, HolidayAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)