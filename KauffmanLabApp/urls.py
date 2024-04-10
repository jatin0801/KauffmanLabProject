from django.urls import path
from KauffmanLabApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("sample_input/", views.sample_input, name="sample_input"),
    path("submit_sample/", views.onSubmitSample, name="submit_sample"),
    path("sample_list/", views.sample_list, name="sample_list"),
    path("sample_csv/", views.sample_csv, name="sample_csv"),
    path("sample_pdf/", views.sample_pdf, name="sample_pdf"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_register, name="register"),
    path("upload_excel/", views.upload_excel, name="upload_excel"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)