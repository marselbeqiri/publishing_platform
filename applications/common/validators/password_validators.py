import re
from django.core.exceptions import ValidationError

__all__ = [
    "UppercaseValidator",
    "SymbolValidator"
]


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                self.get_help_text(),
                code='password_no_upper',
            )

    def get_help_text(self):
        return "Your password must contain at least 1 uppercase letter, A-Z."


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                self.get_help_text(),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return "Your password must contain at least 1 special character: " + "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
