from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'index.html')
def jobdetails(request):
    return render(request,'job_details.html')
def about(request):
    return render(request,'about.html')
def joblisting(request):
    return render(request,'job_listing.html')
def contactus(request):
    return render(request,'contact.html')
