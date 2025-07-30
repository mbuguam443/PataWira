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
    print("Fetched jobs:", job_response.data)
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
    print("combined: ",combined)

    return render(request, "applicationstatus.html", {"applications": combined})

