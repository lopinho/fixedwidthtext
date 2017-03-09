# coding: utf-8
import datetime
import decimal
import unicodedata

import six

from fixedwidthtext import exceptions


class Field(object):
    """Base class for all field types"""

    creation_counter = 0
    default_error_messages = {
        'invalid_choice': 'Value %r is not a valid choice.',
        'null': 'This field cannot be null.',
        'blank': 'This field cannot be blank.'}

    def _init_validate(self):
        if self.size is None:
            raise exceptions.ValidationError('Size cannot be null.')

    def __init__(self, **kwargs):
        self.normalize = kwargs.get('normalize', False)
        self.name = kwargs.get('name', None)
        self.verbose_name = kwargs.get('verbose_name', None)
        self.size = kwargs.get('size', kwargs.get('max_length', None))
        self.choices = kwargs.get('choices', None)
        self.default = kwargs.get('default', None)
        self.static_val = kwargs.get('static_val', None)
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
        exceptions.ValidationError if the data can't be converted.
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
        if self.static_val is not None:
            return self.static_val

        if self.has_default():
            if callable(self.default):
                return self.default()
            return str(self.default)
        return None

    def _check_encoding(self, value):
        if six.PY3 is False:
            value = value.encode('utf-8')
        if self.normalize:
            value = unicodedata.normalize('NFKD', value).encode(
                'ascii', 'ignore')
        return value

    def value_to_string(self, obj):
        """
        Returns a string value of this field from the passed obj.
        Subclasses should implement this.
        """
        pyvalue = self._get_val_from_obj(obj)
        strvalue = self._value_to_string(pyvalue)
        return self._check_encoding(strvalue)

    def _value_to_string(self, val):
        raise NotImplementedError('Need to implement value_to_string.')

    def validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if self.size is None:
            msg = self.error_messages['invalid_size']
            raise exceptions.ValidationError(msg)

        if self.choices:
            options = map(lambda x: x[0], self.choices)
            if value not in options:
                msg = self.error_messages['invalid_choice'] % value
                raise exceptions.ValidationError(msg)

        str_value = self._value_to_string(value)
        if len(str_value) > self.size:
            raise exceptions.ValidationError('Wrong formated size, '
                                             'max size: %s, '
                                             'formated value: %s, '
                                             'formated size: %s' % (
                                                 self.size,
                                                 str_value,
                                                 len(str_value)))

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python and validate are propagated. The correct value is
        returned if no error is raised.
        """
        if value is None:
            value = self.get_default()
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
                        message = message % e.params
                    errors.append(message)
                else:
                    errors.extend(e.messages)
        if errors:
            raise exceptions.ValidationError(errors)

    def _get_val_from_obj(self, obj):
        if self.static_val is not None:
            return self.static_val
        if obj is not None:
            attr = getattr(obj, self.name)
            if attr is not None:
                return getattr(obj, self.name)
            else:
                return self.get_default()


class DateField(Field):
    default_error_messages = {
        'invalid': "'%s' value has an invalid date format. It must be "
        "in 'YYYYMMDD' formated string or instance of datetime.",
        'invalid_date': "'%s' value has the correct format (YYYYMMDD) "
        "but it is an invalid date."}

    def __init__(self, **kwargs):
        kwargs['size'] = 8
        super(DateField, self).__init__(**kwargs)

    def _value_to_string(self, value):
        return self._check_encoding(value.strftime('%Y%m%d'))

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            return datetime.date(
                int(value[:4]), int(value[4:6]), int(value[6:]))
        except Exception:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)


class TimeField(Field):
    default_error_messages = {
        'invalid': "'%s' value has an invalid format. It must be in "
        "HH:MM[:ss[.uuuuuu]] format.",
        'invalid_time': "'%s' value has the correct format "
        "(HH:MM[:ss[.uuuuuu]]) but it is an invalid time."}

    def __init__(self, **kwargs):
        kwargs['size'] = 4
        super(TimeField, self).__init__(**kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, datetime.datetime):
            return value.time()
        try:
            if value is not None:
                if len(value) is 4:
                    parsed = datetime.time(int(value[:2]), int(value[2:]))
                if len(value) is 6:
                    parsed = datetime.time(
                        int(value[:2]), int(value[2:4]), int(value[4:]))
                return parsed
        except ValueError:
            msg = self.error_messages['invalid_time'] % value
            raise exceptions.ValidationError(msg)

    def _value_to_string(self, value):
        return value.strftime("%H%M")


class IntegerField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be an integer or string."}

    def _value_to_string(self, value):
        mask = '%0' + str(self.size) + 'd'
        return mask % int(value)

    def to_python(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, six.string_types) is False:
            raise exceptions.ValidationError(
                self.error_messages['invalid'] % value)
        try:
            return int(value)
        except ValueError:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)


class CharField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be an String."}

    def _value_to_string(self, value):
        current_size = len(value)
        if current_size <= self.size:
            return value + ' ' * (self.size - current_size)
        return value[:self.size]

    def to_python(self, value):
        if isinstance(value, int):
            value = str(value)
        if isinstance(value, six.string_types) is False:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)
        return value.strip()


class StringField(CharField):
    pass


class DecimalField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be a decimal number."}

    def __init__(self, **kwargs):
        super(DecimalField, self).__init__(**kwargs)
        self.decimal_places = kwargs.get('decimal_places', None)

    def _value_to_string(self, value):
        try:
            value = decimal.Decimal(str(value))
            value = str(value.quantize(decimal.Decimal('0.01')))
            value = int(value.replace('.', '').replace(',', ''))
            mask = '%0' + str(self.size) + 'd'
            return mask % value
        except:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)

    def to_python(self, value):
        if self.decimal_places is None:
            raise exceptions.ValidationError('Need to set decimal_places')
        if value is None or isinstance(value, decimal.Decimal):
            return value
        try:
            value = "%s.%s" % (
                value[:-self.decimal_places],
                value[-self.decimal_places:])

            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)
