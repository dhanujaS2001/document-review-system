from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path("", views.dashboard, name="dashboard"),
    path("upload_project/", views.upload_project, name="upload_project"),
    path("review_project/", views.review_project, name="review_project"),
    path("re_upload_doc/", views.re_upload_doc, name="re_upload_doc"),
    path("approved_dashboard/", views.approve_dashboard, name="approve_dashboard"),
    path("update_given_to/", views.update_given_to, name="update_given_to"),
    path("download-all-files/", views.download_all_files, name="download_all_files"),
]