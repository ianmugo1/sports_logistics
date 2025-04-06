from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('logistics_app.urls')),
    # Authentication URLs under "accounts/"
    path('accounts/login/', auth_views.LoginView.as_view(template_name='logistics_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='logistics_app/logout.html'), name='logout'),
    # Password reset URLs
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='logistics_app/password_reset.html'), 
         name='password_reset'),
    path('accounts/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='logistics_app/password_reset_done.html'), 
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='logistics_app/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='logistics_app/password_reset_complete.html'), 
         name='password_reset_complete'),
]
