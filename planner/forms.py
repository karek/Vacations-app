from django import forms
from planner.models import EmailUser, Team
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    # password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = EmailUser
        fields = ('email', 'first_name', 'last_name', 'team', 'is_teamleader')

    # def clean_password2(self):
    #     # Check that the two password entries match
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("Passwords don't match")
    #     return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        # user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = EmailUser
        fields = ('email', 'password', 'first_name', 'last_name', 'team', 'is_active', 'is_admin', 'is_teamleader')
        # fields = ('email', 'first_name', 'last_name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = EmailUser
        fields = ("email", "first_name", "last_name", "team", "holidays")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.team = self.cleaned_data["team"]
        user.holidays = self.cleaned_data["holidays"]
        if commit:
            user.save()
        return user


class YearForm(forms.Form):
    year = forms.DateField(label='Year', input_formats=['%Y'])


class TeamsForm(forms.Form):
    teams = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)