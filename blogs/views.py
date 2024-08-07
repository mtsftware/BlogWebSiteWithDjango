import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from accounts.models import Profile
from blogs.filters import BlogFilter, PageFilter
from blogs.forms import PageForm, BlogForm, TagForm
from blogs.models import Page, Category, Blog, Tag
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse


def index(request):
    blog_filter = BlogFilter(request.GET, queryset=Blog.objects.all().order_by('-created_at'))
    blogs = blog_filter.qs
    if blogs.count() == 0:
        messages.warning(request, 'No posts were found that fit this filter.')
    paginator = Paginator(blogs, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/index.html', {'page_obj': page_obj, 'filter': blog_filter})

def about(request):
    return render(request, 'blogs/about.html')

def search_index(request):
    if 'q' in request.GET and request.GET['q'] != '':
        blogs = Blog.objects.filter(
            Q(title__contains=request.GET['q']) |
            Q(subtitle__contains=request.GET['q']) |
            Q(content__contains=request.GET['q']) |
            Q(tags__title__contains=request.GET['q']) |
            Q(page__title__contains=request.GET['q']) |
            Q(page__category__title__contains=request.GET['q'])
        ).distinct()
    else:
        return HttpResponseRedirect(reverse('index'))
    if blogs.count() == 0:
        messages.warning(request, 'No posts were found that fit this search.')
    paginator = Paginator(blogs, 9)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/index.html', {'page_obj': page_obj, 'filterNotView':True})

def page_view(request):
    page_filter = PageFilter(request.GET, queryset=Page.objects.all().order_by('title'))
    pages = page_filter.qs
    if pages.count() == 0:
        messages.warning(request, 'No pages were found that fit this filter.')
    categories = Category.objects.all()
    paginator = Paginator(pages, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/pages.html', {'categories': categories, 'page_obj': page_obj, 'filter': page_filter})

@login_required
def my_pages_view(request):
    page_filter = PageFilter(request.GET, queryset=Page.objects.filter(creator=request.user).order_by('title'))
    pages = page_filter.qs
    if pages.count() == 0:
        messages.warning(request, 'No pages were found that fit this filter.')
    paginator = Paginator(pages, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/my-pages.html', {'pages': pages, 'page_obj': page_obj, 'filter': page_filter})


@login_required
def create_page_view(request):
    user = request.user
    page = PageForm()
    if not Profile.objects.filter(user=user).exists():
        messages.warning(request, 'You are not allowed to create pages.')
        messages.warning(request, 'Please create your profile first.')
        return HttpResponseRedirect(reverse('create_profile'))
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save(commit=False)
            page.creator = user
            page.save()
            form.save_m2m()
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            messages.success(request, f'{page.title} page has been created')
            return HttpResponseRedirect(reverse('my_pages'))
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

    return render(request, 'blogs/create-page.html', {'page': page})

def page_detail_view(request, page_slug):
    page = get_object_or_404(Page, slug=page_slug)
    blog_filter = BlogFilter(request.GET, queryset=Blog.objects.filter(page=page).order_by('-created_at'))
    blogs = blog_filter.qs
    if blogs.count() == 0:
        messages.warning(request, 'No blogs were found that fit this filter.')
    paginator = Paginator(blogs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blogs/page-detail.html', {'page': page, 'page_obj':page_obj, 'filter':blog_filter})
@login_required
def edit_page_view(request, page_slug):
    page = get_object_or_404(Page, slug=page_slug)
    if page.creator != request.user:
        messages.error(request, 'You dont have permission to edit this page')
        return HttpResponseRedirect(reverse('index'))
    form = PageForm(instance=page)
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
            page.creator = request.user
            if 'image' in request.FILES:
                page.image = request.FILES['image']
            if page.slug == page_slug:
                page.slug = page_slug
            page.save()
            form.save_m2m()
            messages.success(request, f'{page.title} page has been updated')
            return HttpResponseRedirect(reverse('page_detail', args=[page.slug]))
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

    return render(request, 'blogs/edit-page.html', {'form': form,'page': page})

@login_required
def delete_page_view(request, page_slug):
    page = get_object_or_404(Page, slug=page_slug)
    if page.creator == request.user:
        page.delete()
        messages.success(request, 'Page has been deleted successfully.')
        return HttpResponseRedirect(reverse('my_pages'))
    else:
        messages.error(request, 'You do not have permission to delete this page.')
    return HttpResponseRedirect(reverse('page_detail', args=[page.slug]))

@login_required
def post_view(request, page_slug):
    if not Profile.objects.filter(user=request.user).exists():
        messages.error(request, 'You dont have permission to create a blog')
        messages.warning(request, 'You need create a profile')
        return HttpResponseRedirect(reverse('create_profile'))
    page = get_object_or_404(Page, slug=page_slug)
    if page.is_private == True and page.creator != request.user:
        messages.error(request, 'This page is personal')
        return HttpResponseRedirect(reverse('page_detail' , args=[page.slug]))
    blog = BlogForm()
    tag = TagForm()
    if request.method == 'POST':
        if 'blog_submit' in request.POST:
            form_blog = BlogForm(request.POST, request.FILES)
            if form_blog.is_valid():
                blog = form_blog.save(commit=False)
                blog.author = request.user
                blog.page = page
                blog.save()
                form_blog.save_m2m()
                storage = messages.get_messages(request)
                for _ in storage:
                    pass
                return HttpResponseRedirect(reverse('page_detail', args=[page.slug]))
            else:
                for error in form_blog.errors.values():
                    messages.error(request, error.as_text())
                    return HttpResponseRedirect(reverse('post', args=[page.slug]))
        else:
            form_tag = TagForm(request.POST, request.FILES)
            if form_tag.is_valid():
                form_tag.save()
                return HttpResponseRedirect(reverse('post', args=[page.slug]))
            else:
                for error in form_tag.errors.values():
                    messages.error(request, error.as_text())
                    return HttpResponseRedirect(reverse('post', args=[page.slug]))

    return render(request, 'blogs/page-detail.html', {'page': page, 'blog_form': blog, 'tag_form': tag, 'post_view':True})


def blog_detail_view(request, page_slug, blog_slug):
    page = get_object_or_404(Page, slug=page_slug)
    blog = get_object_or_404(Blog, slug=blog_slug)
    return render(request, 'blogs/blog-detail.html', {'page': page, 'blog':blog})
@login_required
def my_blogs_view(request):
    blog_filter = BlogFilter(request.GET, queryset=Blog.objects.filter(author=request.user))
    blogs = blog_filter.qs
    if blogs.count() == 0:
        messages.warning(request, 'No pages were found that fit this filter.')
    paginator = Paginator(blogs, 9)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/my-blogs.html', {'page_obj': page_obj, 'filter': blog_filter})
@login_required
def edit_blog_view(request, page_slug, blog_slug):
    page = get_object_or_404(Page, slug=page_slug)
    blog = get_object_or_404(Blog, slug=blog_slug)
    if blog.author != request.user:
        messages.error(request, 'You dont have permission to edit this blog')
        return HttpResponseRedirect(reverse('blog_detail' , args=[page.slug, blog.slug]))
    blog_form = BlogForm(instance=blog)
    tag_form = TagForm()
    if request.method == 'POST':
        if 'blog_submit' in request.POST:
            blog_form = BlogForm(request.POST, request.FILES, instance=blog)
            if blog_form.is_valid():
                blog = blog_form.save(commit=False)
                blog.updated_at = datetime.datetime.now()
                if blog.slug == blog_slug:
                    blog.slug = blog_slug
                blog.save()
                blog_form.save_m2m()
                storage = messages.get_messages(request)
                for _ in storage:
                    pass
                messages.success(request, 'Blog has been updated')
                return HttpResponseRedirect(reverse('blog_detail', args=[page.slug, blog.slug]))
            else:
                for error in blog_form.errors.values():
                    messages.error(request, error.as_text())
        else:
            tag_form = TagForm(request.POST, request.FILES)
            if tag_form.is_valid():
                tag_form.save()
                return HttpResponseRedirect(reverse('blog_edit', args=[page.slug, blog.slug]))
            else:
                for error in tag_form.errors.values():
                    messages.error(request, error.as_text())

    return render(request, 'blogs/page-detail.html', {'blog_form': blog_form, 'tag_form': tag_form, 'page': page, 'post_view':True, 'edit':True})

@login_required
def delete_post_view(request, page_slug, blog_slug):
    page = get_object_or_404(Page, slug=page_slug)
    blog = get_object_or_404(Blog, slug=blog_slug)
    if blog.author == request.user:
        blog.delete()
        return HttpResponseRedirect(reverse('blog_detail', args=[page.slug, blog.slug]))
    else:
        messages.error(request, 'You dont have permission to delete this blog')
        return HttpResponseRedirect(reverse('blog_detail', args=[page.slug, blog.slug]))

def write_view(request):
    page_filter = PageFilter(request.GET, queryset=Page.objects.all().order_by('title'))
    pages = page_filter.qs
    if pages.count() == 0:
        messages.warning(request, 'No pages were found that fit this filter.')
    categories = Category.objects.all()
    paginator = Paginator(pages, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/pages.html', {'categories': categories, 'page_obj': page_obj, 'selectPage': True, 'filter': page_filter})

def tag_view(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    blogs = Blog.objects.filter(tags__slug=tag_slug)
    if blogs.count() == 0:
        messages.warning(request, 'No blogs were found that fit this tag.')
        return HttpResponseRedirect(reverse('index'))
    paginator = Paginator(blogs, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/index.html', {'page_obj':page_obj, 'filterNotView': True})

def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    page = Page.objects.filter(category=category)
    if page.count() == 0:
        messages.warning(request, 'No pages were found that fit this category.')
        return HttpResponseRedirect(reverse('index'))
    paginator = Paginator(page, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'blogs/pages.html', {'page_obj':page_obj, 'filterNotView': True})




# Create your views here.
