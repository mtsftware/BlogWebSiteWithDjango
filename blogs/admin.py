from django.contrib import admin
from .models import Category, Page, Tag, Blog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('title',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('creator', 'title', 'slug', 'is_private')
    search_fields = ('title', 'creator__username')
    list_filter = ('is_private', 'category')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('title',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'blog_count')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}

    def blog_count(self, obj):
        return obj.blog_set.count()

    blog_count.short_description = 'Blog Count'
    ordering = ('title',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'author', 'page', 'is_published', 'is_private', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle', 'author__username', 'content')
    list_filter = ('is_published', 'is_private', 'tags', 'page')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')