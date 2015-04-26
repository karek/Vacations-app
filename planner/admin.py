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
    ordering = ('team', 'last_name', 'first_name', 'email')
    filter_horizontal = ()


class HolidayAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(HolidayAdmin, self).get_urls()
        my_urls = patterns('', url(r'^add_weekend/$', YearFormView.as_view(), name='planner_holiday_add_weekend')
        )
        return my_urls + urls

    change_list_template = 'planner/change_list.html'
    list_display = ('name', 'day')
    ordering = ('-day', 'name')


class EmailUserInline(admin.TabularInline):
    model = EmailUser
    fields = ['email', 'first_name', 'last_name', 'is_teamleader']
    template = 'admin/tabular.html'
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [EmailUserInline]
    list_display = ('name', 'member_count', 'has_teamleader')

    def member_count(self, obj):
        return obj.emailuser_set.count()

    def has_teamleader(self, obj):
        teamleaders = obj.emailuser_set.filter(is_teamleader=True)
        return teamleaders.exists()

    has_teamleader.boolean = True


class AbsenceRangeAdmin(admin.ModelAdmin):
    fieldsets = (
        # ('Absence', {'fields': ('absence',)}),
        ('Day range', {'fields': ('begin', 'end',)}),
    )
    # TODO display how many working days in the absence range
    list_display = ('begin', 'end', 'absence')
    ordering = ('-begin', '-end')


class AbsenceRangeInline(admin.TabularInline):
    model = AbsenceRange
    fields = ['begin', 'end']
    template = 'admin/tabular.html'
    extra = 1


class AbsenceAdmin(admin.ModelAdmin):
    # TODO display how many working days in the absence
    list_display = ('user', 'first_day', 'last_day', 'ranges', 'absence_kind', 'status')
    fieldsets = (
        ('Basic information', {'fields': ('user', 'absence_kind')}),
        ('Status', {'fields': ('status',)})
    )
    inlines = [AbsenceRangeInline]

    def first_day(self, obj):
        first_range = obj.absencerange_set.earliest('begin')
        return first_range.begin

    def last_day(self, obj):
        last_range = obj.absencerange_set.latest('end')
        return last_range.end


    def ranges(self, obj):
        return obj.absencerange_set.count()


class AbsenceKindAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic information', {'fields': ('name',)}),
        ('Acceptance', {'fields': ('require_acceptance',)}),
        ('Display', {'fields': ('text_color', 'bg_color',)}),
    )
    list_display = ('name', 'require_acceptance', 'text_color', 'bg_color')


admin.site.register(EmailUser, EmailUserAdmin)
admin.site.register(Absence, AbsenceAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(AbsenceRange, AbsenceRangeAdmin)
admin.site.register(AbsenceKind, AbsenceKindAdmin)
admin.site.register(Holiday, HolidayAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
