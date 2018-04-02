from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from baratico.models import Usuario


class RegistroForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username',
                'email',
                'password']
