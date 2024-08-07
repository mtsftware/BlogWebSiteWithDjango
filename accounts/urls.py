from django.contrib.auth.views import PasswordResetConfirmView
from django.views.generic import TemplateView

from . import views
from django.urls import path

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    path('account_activation_sent/', TemplateView.as_view(template_name="accounts/account_activation_sent.html"),
         name='account_activation_sent'),
    path('logout', views.logout_view, name='logout'),
    path('profile/create-profile', views.create_profile_view, name='create_profile'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('profile/<str:username>/edit-profile', views.edit_profile_view, name='edit_profile'),
    path('password_change', views.password_change_view, name='password_change'),
    path('password_reset', views.password_reset_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]