from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class PasswordlessAuthBackend(ModelBackend):
    # FIXME Add token verification to make sure a view can authenticate user without password?

    user_model = get_user_model()

    def authenticate(self, email=None):
        try:
            return self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None