# coding: utf-8
import datetime
import decimal

from fixedwidthtext import exceptions


class Field(object):
    """Base class for all field types"""

    creation_counter = 0
    default_error_messages = {
        'invalid_choice': 'Value %r is not a valid choice.',
        'null': 'This field cannot be null.',
        'blank': 'This field cannot be blank.',
    }

    def _init_validate(self):
        if self.size is None:
            raise exceptions.ValidationError('Size cannot be null.')

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.verbose_name = kwargs.get('verbose_name', None)
        self.size = kwargs.get('size', None)
        self.choices = kwargs.get('choices', None)
        self.default = kwargs.get('default', None)
        self.validators = kwargs.get('validators', [])
        error_messages = kwargs.get('error_messages', None)

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        # Adjust the appropriate creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1
        self._init_validate()

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        fixedwidthtext.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should implement this.
        """
        raise NotImplementedError('Need to implement to_python.')

    def get_verbose_name(self):
        if self.verbose_name:
            return self.verbose_name
        return self.name.replace('_', ' ')

    def to_dict(self, object):
        return {
            'name': self.name,
            'verbose_name': self.get_verbose_name(),
            'value': self.to_python(getattr(object, self.name))
        }

    def has_default(self):
        """
        Returns a boolean of whether this field has a default value.
        """
        return self.default is not None

    def get_default(self):
        """
        Returns the default value for this field.
        """
        if self.has_default():
            if callable(self.default):
                return self.default()
            return str(self.default)
        return ""

    def value_to_string(self, obj):
        """
        Returns a string value of this field from the passed obj.
        Subclasses should implement this.
        """
        raise NotImplementedError('Need to implement value_to_string.')

    def validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if self.size is None:
            msg = self.error_messages['invalid_size']
            raise exceptions.ValidationError(msg)

        if self.choices and value not in choices:
            msg = self.error_messages['invalid_choice'] % value
            raise exceptions.ValidationError(msg)

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python and validate are propagated. The correct value is
        returned if no error is raised.
        """
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value

    def run_validators(self, value):
        errors = []
        for validator in self.validators:
            try:
                validator(value)
            except exceptions.ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    message = self.error_messages[e.code]
                    if e.params:
                        mesage = message % e.params
                    error.append(message)
                else:
                    errors.extend(e.messages)
        if errors:
            raise exceptions.ValidationError(errors)

    def _get_val_from_obj(self, obj):
        if obj is not None:
            return getattr(obj, self.name)
        else:
            return self.get_default()


class DateField(Field):
    default_error_messages = {
        'invalid': "'%s' value has an invalid date format. It must be "
                     "in YYYYMMDD format.",
        'invalid_date': "'%s' value has the correct format (YYYYMMDD) "
                          "but it is an invalid date.",
    }
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.strftime('%Y%m%d')

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            return datetime.date(
                int(value[:4]), int(value[4:6]), int(value[6:]))
        except ValueError:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)

class IntegerField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be an integer.",
    }
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        mask = '%0' + str(self.size) + 'd'
        return mask % value

    def to_python(self, value):
        try:
            return int(value)
        except ValueError:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)


class StringField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be an String.",
    }
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        current_size = len(value)
        if current_size <= self.size:
            return value + ' ' * (self.size - current_size)
        return value[:self.size]

    def to_python(self, value):
        if isinstance(value, (str, unicode)) is False:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)
        return value.strip()


class DecimalField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be a decimal number.",
    }

    def __init__(self, **kwargs):
        super(DecimalField, self).__init__(**kwargs)
        self.decimal_places = kwargs.get('decimal_places', None)

    def value_to_string(self, obj):
        value = str(self._get_val_from_obj(obj))
        value = int(value.replace('.', '').replace(',', ''))
        mask = '%0' + str(self.size) + 'd'
        return mask % value

    def to_python(self, value):
        if value is None:
            return value
        try:
            value = "%s.%s" % (
                value[:-self.decimal_places],
                value[-self.decimal_places:])

            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)
