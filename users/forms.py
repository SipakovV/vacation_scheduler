import logging

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import CustomUser

logger = logging.getLogger(__name__)


class CustomUserCreationForm(UserCreationForm):

    def clean(self):
        cleaned_data = super(CustomUserCreationForm, self).clean()
        logger.debug('CreationForm.Clean(): ' + str(cleaned_data.get('is_staff')) + str(cleaned_data.get('bound_employee')))
        if not (self.fields['is_staff'] or self.fields['is_superuser'] or self.fields['bound_employee']):
            logger.debug('Validation')
            raise ValidationError('Пользователь должен обладать правами персонала или иметь связанного сотрудника')
        return cleaned_data

    class Meta:
        model = CustomUser
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):

    def clean(self):
        cleaned_data = super(CustomUserChangeForm, self).clean()
        logger.debug('ChangeForm.Clean(): ' + str(cleaned_data.get('is_staff')) + str(cleaned_data.get('bound_employee')))

        logger.debug(str(bool(cleaned_data.get('is_staff'))) + ' ' + str(bool(cleaned_data.get('bound_employee'))))

        if not (cleaned_data.get('is_staff') or cleaned_data.get('bound_employee')):
            logger.debug('Validation')
            raise ValidationError('Пользователь должен обладать правами персонала или иметь связанного сотрудника')
        return cleaned_data


    class Meta:
        model = CustomUser
        fields = ('username',)
