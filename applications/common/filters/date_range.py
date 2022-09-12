from django_filters import RangeFilter
from django_filters.fields import DateRangeField as ParentDateRangeField
from django_filters.widgets import RangeWidget


class DateRangeWidget(RangeWidget):
    suffixes = ["start", "end"]

    def suffixed(self, name, suffix):
        return "_".join([suffix, name]) if suffix else name


class DateRangeField(ParentDateRangeField):
    widget = DateRangeWidget


class DateFromToRangeFilter(RangeFilter):
    field_class = DateRangeField
