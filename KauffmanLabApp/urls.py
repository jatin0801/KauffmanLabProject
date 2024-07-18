from django.urls import path
from KauffmanLabApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("admin_panel/", views.admin_panel, name="admin_panel"),
    path('sample_list/<str:sample_id>/edit/', views.sample_edit, name='sample_edit'),
    path('sample_list/<str:sample_id>/discard/', views.sample_discard, name='sample_discard'),
    path("sample_list/", views.sample_list, name="sample_list"),
    path("sample_pdf/", views.sample_pdf, name="sample_pdf"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_register, name="register"),
    path("upload_excel/", views.upload_excel, name="upload_excel"),
    path('sample_list/<str:pk>/', views.sample_detail, name='sample_detail'),
    path('form/<str:form_group>/', views.form_view, name='form_view'),
    path('download_excel_template/', views.download_excel_template, name='download_excel_template'),
    path('backup-and-upload/', views.backup_and_upload, name='backup_and_upload'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)