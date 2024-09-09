from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('home/', views.home_view, name='home'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PassworetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.account_update_view, name='account_update'),
    path('profile/upload-image/', views.profile_image_upload, name='profile_image_upload'),
    path('profile/update/confirmation', views.account_update_confirmation_view, name='account_update_confirmation'),
    path('profile/account_delete', views.account_delete_view, name='account_delete'),
    path('flashcard_sets/', views.flashcard_set_list_view, name='flashcard_set_list'), # list of flashcard sets
    path('flashcard_sets/create/', views.create_flashcard_set_view, name='create_flashcard_set'), # create a new flashcard set
    path('flashcard_sets/<int:set_id>/', views.flashcard_set_detail_view, name='flashcard_set_detail'), # view flashcard set details
    path('flashcard_sets/<int:set_id>/edit/', views.update_flashcard_set_view, name='edit_flashcard_set'), # update flashcard set details
    path('flashcard_sets/<int:set_id>/delete/', views.delete_flashcard_set_view, name='delete_flashcard_set'), # delete flashcard set
    path('flashcard_sets/selection/', views.flashcard_set_selection_view, name='flashcard_set_selection'), # where the user selects which flashcard set they're going to use
    path('generate-content/<str:set_name>/', views.generate_content_view, name='generate_content'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)