import os
import zipfile
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from accounts.models import User
from .models import Project,generate_project_code, replace_file


def dashboard(request):
    user = User.objects.all()
    projects = Project.objects.exclude(status="APPROVED").order_by("-id")

    return render(
        request,
        "dashboard.html",
        context={
            "projects": projects,
            "authors": user
        }
    )
    
def upload_project(request):
    if request.method == "POST":
        try:
            print(request.POST)
            uploaded_by = request.POST["uploaded_by"]
            description = request.POST["description"]
            document = request.FILES["project_document"]

            uploaded_user = User.objects.get(id=uploaded_by)
            project_code = generate_project_code(uploaded_user)
            Project.objects.create(
                project_code=project_code,
                description=description,
                project_document=document,
                uploaded_by=uploaded_user
            )
            try:
                send_mail(
                    subject=f"New Project Uploaded: {project_code}",
                    message=(
                        f"A new project has been uploaded.\n\n"
                        f"Project Code: {project_code}\n"
                        f"Uploaded By: {uploaded_user.get_full_name()}\n"
                        f"Description: {description}"
                    ),
                    from_email=None,  # uses DEFAULT_FROM_EMAIL
                    recipient_list=["muhsinsulaiman689@gmail.com"],  
                    fail_silently=False,
                )
            except Exception as e:
                print(request, f"Project uploaded but failed to send email: {e}")
            messages.success(request, f"Project {project_code} uploaded successfully.")

        except User.DoesNotExist:
            messages.error(request, "Selected author does not exist.")
        except Exception as e:
            messages.error(request, f"Something went wrong while uploading: {e}")
    
    return redirect("dashboard")


def review_project(request):

    if request.method == "POST":
        try:
            
            print(request.POST)
            review_doc = request.FILES.get("review_document")
            project = Project.objects.get(pk=request.POST["project_id"])
            project.reviewed_by = User.objects.get(username='muhsin')
            if project.review_document and review_doc:
                replace_file(project.review_document, review_doc)
            else:
                project.review_document = review_doc
            project.review_description = request.POST.get("review_description")
            project.status = request.POST.get("status")
            project.save()
            if project.status == "APPROVED":
                try:
                    send_mail(
                        subject=f"Project Approved: {project.project_code}",
                        message=(
                            f"Your project has been approved.\n\n"
                            f"Project Code: {project.project_code}\n"
                            f"Description: {project.description}"
                        ),
                        from_email=None,  # uses DEFAULT_FROM_EMAIL
                        recipient_list=[project.uploaded_by.email],  
                        fail_silently=False,
                    )
                except Exception as e:
                    print(request, f"Project approved but failed to send email: {e}")
            else:
                try:
                    send_mail(
                        subject=f"Review document of Project is Uploaded: {project.project_code}",
                        message=(
                            f"A Review document of Project has been uploaded.\n\n"
                            f"Project Code: {project.project_code}\n"
                            f"Description: {project.review_description}"
                        ),
                        from_email=None,  # uses DEFAULT_FROM_EMAIL
                        recipient_list=[project.uploaded_by.email],  
                        fail_silently=False,
                    )
                except Exception as e:
                    print(request, f"Review document uploaded but failed to send email: {e}")
                messages.success(request, f"Review for {project.project_code} saved.")

        except Project.DoesNotExist:
            messages.error(request, "Project not found.")
        except User.DoesNotExist:
            messages.error(request, "Reviewer account not found.")
        except Exception as e:
            messages.error(request, f"Something went wrong while saving the review: {e}")

    return redirect("dashboard")

def re_upload_doc(request):

    if request.method == "POST":
        try:
            print(request.POST)
            project = Project.objects.get(pk=request.POST["project_id"])
            re_upload_doc = request.FILES.get("project_document")
            if re_upload_doc:
                replace_file(project.project_document, re_upload_doc)
            project.description = request.POST.get("edit_description")
            project.status = "READY"
            project.save()
            try:
                send_mail(
                    subject=f"Updated version of Project Uploaded: {project.project_code}",
                    message=(
                        f"A Updated version of Project has been uploaded.\n\n"
                        f"Project Code: {project.project_code}\n"
                        f"Uploaded By: {project.uploaded_by.get_full_name()}\n"
                        f"Description: {project.description}"
                    ),
                    from_email=None,  # uses DEFAULT_FROM_EMAIL
                    recipient_list=["muhsinsulaiman689@gmail.com"],  
                    fail_silently=False,
                )
            except Exception as e:
                print(request, f"Project re-uploaded but failed to send email: {e}")
            messages.success(request, f"Project {project.project_code} updated.")

        except Project.DoesNotExist:
            messages.error(request, "Project not found.")
        except Exception as e:
            messages.error(request, f"Something went wrong while re-uploading: {e}")


    return redirect("dashboard")


def approve_dashboard(request):
    approved_projects = Project.objects.filter(status="APPROVED").order_by("-id")
    return render(
        request,
        "approved_dashboard.html",
        context={
            "approved_projects": approved_projects
        }
    )
    
def update_given_to(request):
    if request.method == "POST":
        print(request.POST)
        try:
            project_id = request.POST.get("project_id")
            given_to = request.POST.get("given_to")

            project = Project.objects.get(pk=project_id)
            project.given_to = given_to
            project.save()

            messages.success(request, f"Project {project.project_code} is Given To {project.given_to}.")

        except Project.DoesNotExist:
            messages.error(request, "Project not found.")
        except Exception as e:
            messages.error(request, f"Something went wrong while updating: {e}")

    return redirect("approve_dashboard")

def download_all_files(request):
    approved_projects = Project.objects.filter(status="APPROVED").order_by("-id")

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for project in approved_projects:

            if project.project_document:
                file_path = project.project_document.path

                if os.path.exists(file_path):

                    filename = os.path.basename(file_path)

                    zip_file.write(file_path, arcname=filename)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/zip"
    )

    response["Content-Disposition"] = 'attachment; filename="Approved_Documents.zip"'

    return response

def download_all_ready_files(request):
    ready_projects = Project.objects.filter(status="READY").order_by("-id")

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for project in ready_projects:

            if project.project_document:
                file_path = project.project_document.path

                if os.path.exists(file_path):

                    filename = os.path.basename(file_path)

                    zip_file.write(file_path, arcname=filename)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/zip"
    )

    response["Content-Disposition"] = 'attachment; filename="Ready_Documents.zip"'

    return response

