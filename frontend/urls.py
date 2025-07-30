from django.urls import path
from . import views


urlpatterns=[
    path('',views.home,name='home'),
    path('jobdetails/<int:id>/',views.jobdetails,name='jobdetails'),
    path('about',views.about,name='about'),
    path('joblisting',views.joblisting,name='joblisting'),
    path('contactus',views.contactus,name='contactus'),
    path("search/", views.job_search, name="job_search"),
]