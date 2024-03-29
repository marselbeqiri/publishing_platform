from rest_framework import serializers


class LabelChoiceField(serializers.ChoiceField):

    def to_representation(self, value):
        """
        This override make possible on Read actions to display the label of the selected Value.
        """
        if value in ('', None):
            return value
        choice_strings_to_values = {
            str(key): label for key, label in self.choices.items()
        }
        return choice_strings_to_values.get(str(value), value)


class NonNullableCharField(serializers.CharField):
    def get_value(self, data):
        """
            If field have allow_blank=True passed as arg,
            nullable values will be replaced by default value ("" or passed default=value)
        """
        if self.allow_blank:
            if self.field_name not in data:
                return self.default
            return data.get(self.field_name) or ""
        return super(NonNullableCharField, self).get_value(data)
