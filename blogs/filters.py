import django_filters

from blogs.models import Blog, Category, Tag, Page


class BlogFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug',
        label='Tags',
    )
    class Meta:
        model = Blog
        fields = ['page','tags']

class PageFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        to_field_name='slug',
        field_name='category__slug',
        label='Categories',
    )
    is_private = django_filters.BooleanFilter(
        field_name='is_private',
        label='Personal',
    )
    class Meta:
        model = Page
        fields = ['category', 'is_private']