from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('/', views.search_index, name='searchIndex'),
    path('pages/create-page', views.create_page_view, name='create_page'),
    path('pages/my-pages', views.my_pages_view, name='my_pages'),
    path('pages/', views.page_view, name='page'),
    path('write/', views.write_view, name='write'),
    path('pages/<slug:page_slug>/', views.page_detail_view, name='page_detail'),
    path('pages/<slug:page_slug>/delete', views.delete_page_view, name='delete_page'),
    path('pages/<slug:page_slug>/edit', views.edit_page_view, name='edit_page'),
    path('pages/<slug:page_slug>/post', views.post_view, name='post'),
    path('my-blogs/', views.my_blogs_view, name='my-blogs'),
    path('pages/<slug:page_slug>/<slug:blog_slug>', views.blog_detail_view, name='blog_detail'),
    path('pages/<slug:page_slug>/<slug:blog_slug>/edit', views.edit_blog_view, name='blog_edit'),
    path('pages/<slug:page_slug>/<slug:blog_slug>/delete', views.delete_post_view, name='blog_delete'),
    path('tags/<slug:tag_slug>', views.tag_view, name='tags'),
    path('categories/<slug:category_slug>', views.category_view, name='category'),
]