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

