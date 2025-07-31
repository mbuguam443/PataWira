from django.urls import path
from . import views


urlpatterns=[
    path('',views.home,name='home'),
    path('jobdetails/<int:id>/',views.jobdetails,name='jobdetails'),
    path('about',views.about,name='about'),
    path('joblisting',views.joblisting,name='joblisting'),
    path('contactus',views.contactus,name='contactus'),
    path("search/", views.job_search, name="job_search"),
    path("login/", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("loginsubmit/", views.login_view, name="loginsubmit"),
    path("logout/", views.logout_view, name="logout"),
    path("signupsubmit/", views.signup_view, name="signupsubmit"),
    path("applynow/<int:id>/",views.Applynow,name="applynow"),
    path("applycomplete",views.ApplyComplete,name="applycomplete"),
    path("submit-application/", views.submit_application_view, name="submit_application"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("postjob/", views.PostJobs, name="postjob"),
    path('post-job/', views.create_job, name='create_job'),
    path("jobs/edit/<int:job_id>/", views.edit_job, name="edit_job"),

    path("editjob/<int:id>/", views.EditJob, name="editjob"),
    path("jobs/delete/<int:job_id>/", views.delete_job, name="delete_job"),
    path("managejob/", views.ManageJob, name="managejob"),
    path("manageapplication", views.ManageApplication, name="manageapplication"),
    path("applications/update/<int:app_id>/", views.update_application_status, name="update_application_status"),

]