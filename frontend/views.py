import json
from django.shortcuts import redirect, render
from supabase import create_client
from dotenv import load_dotenv
import os
import re
from django.contrib import messages
from frontend.login_required_supabase import login_required_supabase




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
    request.session["last_step"] = request.path
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


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print("email: ",email)
        print("password: ",password)
        try:
            res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password,
            })
            
            user = res.user
            if user:
                    request.session["user"] = user.id
                    request.session["email"] = user.email
                    print("user : ", user.email)
                    redirect_to = request.session.pop("last_step", "/")
                    messages.success(request, "Login success.")
                    return redirect(redirect_to)
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")    
            return redirect("/login/")

def login(request):

    return render(request,'login.html')
#@login_required_supabase
def signup(request):
    return render(request,'signup.html')

def logout_view(request):
    request.session.flush()  # Clears all session data
    return redirect("/login/")  # Redirect to login page or homepage    

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")

        try:
            result = supabase.auth.sign_up({
                "name":"mathew",
                "phone":"075366564",
                "email": email,
                "password": password
            })
            print("result: ",result)
            # Optionally: store user info or send email confirmation
            if result.user:
                messages.success(request, "Registration successful. Please check your email to confirm.")
                return redirect("login")  # Or wherever
            else:
                messages.error(request, "Signup failed.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "signup.html")

def Applynow(request,id):

    return render(request,'applynow.html',{"jobid":id})

def ApplyComplete(request):
    return render(request,'applycomplete.html')

def submit_application_view(request):
    if request.method == "POST":
        job_id = request.POST.get("job_id")
        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        email = request.session["email"]

        # Insert into Supabase
        data = {
            "job_id": job_id,
            "full_name": full_name,
            "phone_number": phone_number,
            "email": email,
        }
        try:
            supabase.table("applications").insert(data).execute()
            messages.success(request, "Applied successufully.")
            return render(request, "applycomplete.html")
        except Exception as e:
            messages.success(request, "You have Already Applied this job.")
            return render(request, "applycomplete.html")    
         # Or redirect
    return redirect("/")

def my_applications(request):
    email = request.session.get("email")
    if not email:
        return redirect("login")

    # Step 1: Get all applications by the user
    app_response = supabase.table("applications").select("job_id, full_name, phone_number, email,status,created_at").eq("email", email).execute()
    applications = app_response.data
    print("Applications:", applications)
    job_ids = list(set([app["job_id"] for app in applications]))  # Unique job IDs

    # Step 2: Fetch job details for those job_ids
    job_response = supabase.table("job_posts").select("id, title, company_name, location").in_("id", job_ids).execute()
    job_map = {job["id"]: job for job in job_response.data}
    # print("Fetched jobs:", job_response.data)
    # Step 3: Combine application + job info
    combined = []
    for app in applications:
        job = job_map.get(app["job_id"])
        if job:
            combined.append({
                "job_title": job["title"],
                "company_name": job.get("company_name", ""),
                "status": app["status"],
                "location":job["location"],
                "appliedon": app["created_at"],
            })
    #print("combined: ",combined)

    return render(request, "applicationstatus.html", {"applications": combined})

def PostJobs(request):
    return render(request,'post_jobs.html')

def EditJob(request):
    return render(request,'edit_jobs.html')

def ManageJob(request):
    query = request.GET.get("q", "").strip().lower()

    response = supabase.table("job_posts").select("*").execute()
    jobs = response.data if response.data else []

    if query:
        def match(job):
            return (
                query in job.get("title", "").lower()
                or query in job.get("company_name", "").lower()
                or query in job.get("location", "").lower()
                or query in job.get("category", "").lower()
                or any(query in s.lower() for s in job.get("skills", []))
            )
        jobs = list(filter(match, jobs))
    return render(request,'manage_jobs.html',{"jobs": jobs})

def ManageApplication(request):
    query = request.GET.get("q", "").lower()  # user search input

    # Fetch all applications
    applications_response = supabase.table("applications").select("*").execute()
    applications = applications_response.data

    # Fetch job titles
    jobs_response = supabase.table("job_posts").select("id, title").execute()
    job_map = {job["id"]: job["title"] for job in jobs_response.data}

    # Add job title to each application
    for app in applications:
        app["job_title"] = job_map.get(app["job_id"], "Unknown")

    # Filter based on search query
    if query:
        applications = [
            app for app in applications if
            query in app.get("full_name", "").lower() or
            query in app.get("email", "").lower() or
            query in app["job_title"].lower()
        ]
    #print("applications: ",applications)
    return render(request, "manage_application.html", {
        "applications": applications,
        "search_query": query
    })

def create_job(request):
    if request.method == "POST":
        print("category: ",request.POST.get("category", "")) 
        data = {
            "Category": request.POST.get("category", ""),
            "title": request.POST.get("title"),
            "company_name": request.POST.get("company_name"),
            "location": request.POST.get("location"),
            "salary_range": request.POST.get("salary_range"),
            "job_description": request.POST.get("job_description"),
            "skills": request.POST.get("skills", "").strip(),        # e.g. "Strength, Teamwork"
            "experience": request.POST.get("experience", "").strip(), # e.g. "1 year, 2 years"
            "application_deadline": request.POST.get("application_deadline"),
            "job_nature": request.POST.get("job_nature"),
            "yearly_salary": int(request.POST.get("yearly_salary")),
            "vacancy": int(request.POST.get("vacancy")),
        }

        supabase.table("job_posts").insert(data).execute()
        messages.success(request, "Posted successfully !.")
        return redirect("postjob")  # or wherever you list jobs

    return render(request, "post_jobs.html")  # this should match your form template


def delete_job(request, job_id):
    if request.method == "GET":
        supabase.table("job_posts").delete().eq("id", job_id).execute()
    return redirect("managejob")

def edit_job(request, job_id):
    # 1. Get job from Supabase
    response = supabase.table("job_posts").select("*").eq("id", job_id).execute()
    job = response.data[0] if response.data else None

    if request.method == "POST":
        # 2. Update the job with form data
        print("Category: ",request.POST.get("category", "").strip())
        updated_data = {
            "title": request.POST.get("title"),
            "company_name": request.POST.get("company_name"),
            "location": request.POST.get("location"),
            "salary_range": request.POST.get("salary_range"),
            "job_description": request.POST.get("job_description"),
            "skills": request.POST.get("skills", "").strip(),
            "experience": request.POST.get("experience", "").strip(),
            "application_deadline": request.POST.get("application_deadline"),
            "job_nature": request.POST.get("job_nature"),
            "yearly_salary": int(request.POST.get("yearly_salary")),
            "vacancy": int(request.POST.get("vacancy")),
            "Category": request.POST.get("category", "").strip(),
        }

        supabase.table("job_posts").update(updated_data).eq("id", job_id).execute()
        return redirect("managejob")

    return render(request, "edit_jobs.html", {"job": job}) 

from collections import Counter
def home(request):
    # Fetch all job categories from Supabase (ensure column name matches Supabase exactly)
    response = supabase.table('job_posts').select('Category').execute()

    # If Supabase uses 'Category' (capital C), access it exactly like that
    categories = [job['Category'] for job in response.data if job.get('Category')]

    # Count how many jobs per category
    category_counts = dict(Counter(categories))  # Ensure it's a dict, not just Counter object

    #print("category_counts =", category_counts)

    return render(request, 'index.html', {
        'category_counts': category_counts
    }) 


def update_application_status(request, app_id):
    if request.method == "POST":
        new_status = request.POST.get("status")

        # Update in Supabase
        supabase.table("applications").update({"status": new_status}).eq("id", app_id).execute()

    return redirect("manageapplication")   