from django.shortcuts import redirect

def login_required_supabase(view_func):
    def wrapper(request, *args, **kwargs):
        if "user" not in request.session:
            return redirect("login")  # Or wherever your login page is
        return view_func(request, *args, **kwargs)
    return wrapper
