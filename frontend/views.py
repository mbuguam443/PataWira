from django.shortcuts import render
from supabase import create_client
from dotenv import load_dotenv
import os
import re



load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create your views here.
def home(request):
    response = supabase.table("job_posts").select("*").execute()
    jobs = response.data

    # Extract unique locations
    all_locations = [job.get("location") for job in jobs if job.get("location")]
    unique_locations = sorted(set(all_locations))  # remove duplicates and sort

    
    
    return render(request,'index.html', {
        "todos": jobs,
        "locations": unique_locations,
    })
def jobdetails(request,id):
    todo = supabase.table("job_posts").select("*").eq("id", id).execute().data[0]
    skills = todo["skills"] 
    skills_list = re.findall(r'"?([^",{}]+)"?', skills)
    skills_list = [item.strip('"') for item in skills_list]

    experience = todo["experience"] 
    experience_list = re.findall(r'"?([^",{}]+)"?', experience)
    experience_list = [item.strip('"') for item in experience_list]

    return render(request,'job_details.html',{"todo": todo,"skills_list":skills_list,"experience_list":experience_list})
def about(request):
    return render(request,'about.html')
def joblisting(request):
    query = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    query = request.GET.get("q", "")
    
    if query:
        response = supabase.table("job_posts") \
            .select("*") \
            .ilike("title", f"%{query}%") \
            .execute()
    else:
        response = supabase.table("job_posts").select("*").execute()
    
    jobs = response.data
    count=len(jobs)
    return render(request, "job_listing.html", {"todos": jobs, "query": query,"count":count})
def contactus(request):
    return render(request,'contact.html')

def job_search(request):
    query = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    
    if query:
        response = supabase.table("job_posts") \
            .select("*") \
            .ilike("title", f"%{query}%") \
            .execute()
    else:
        response = supabase.table("job_posts").select("*").execute()
    
    jobs = response.data
    count=len(jobs)
    return render(request, "job_listing.html", {"todos": jobs, "query": query,"count":count})

