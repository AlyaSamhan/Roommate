from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from advertisements.models import Advertisement
from .models import Favorite ,Profile ,Validation
from advertisements.models import Advertisement
from django.db import IntegrityError
# Create your views here.


def register_user_view(request: HttpRequest):
    msg = None

    if request.method == "POST":
        try:
        
            user = User.objects.create_user(username=request.POST["username"], first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=request.POST["password"])
            user.save()
            return redirect("accounts:login_user_view")
       
        except IntegrityError as e:
            msg = f"Please select another username"
        except Exception as e:
            msg = f"something went wrong {e}"

    return render(request, "accounts/register.html", {"msg" : msg})


def login_user_view(request: HttpRequest):
    msg = None
    if request.method == "POST":
       user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
       if user:
           login(request, user)
           return redirect("main:home_page")
       else:
          msg = "Please provide correct username and password"
    return render(request, "accounts/login.html", {"msg" : msg})


def logout_user_view(request: HttpRequest):
     if request.user.is_authenticated:
        logout(request) 
     return redirect("accounts:login_user_view")



def user_profile(request: HttpRequest, user_id):

    try:
        user = User.objects.get(id=user_id)
    except:
        return render(request, 'main/not_found.html')
    return render(request, 'accounts/profile.html', {"user":user})


def update_user_view(request: HttpRequest):
    msg = None
 
    if request.method == "POST":
        try:
            if request.user.is_authenticated:
                user : User = request.user
                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.email = request.POST["email"]
                user.save()

                try:
                    profile : Profile = request.user.profile
                except Exception as e:
                    profile = Profile(user=user)
     

                if 'personal_image' in request.FILES: profile.personal_image = request.FILES["personal_image"]
                profile.phone_number = request.POST["phone_number"]
                profile.gender = request.POST["gender"]
                profile.age = request.POST["age"]
                profile.about = request.POST["about"]
                profile.language = request.POST["language"]
                profile.nationality = request.POST["nationality"]
                profile.save()

                return redirect("accounts:user_profile", user_id = request.user.id)

            else:
                return redirect("accounts:login_user_view")
        except IntegrityError as e:
            print(e)
            msg = f"Please select another username"
        except Exception as e:
            msg = f"something went wrong {e}"

    return render(request, "accounts/update.html", {"msg" : msg})



def add_favorite(request:HttpRequest, advertisement_id):

    if not request.user.is_authenticated:
        return redirect("accounts:login_user_view")

    try:
        advertisement = Profile.objects.get(id=advertisement_id)
        user_favored = Favorite.objects.filter(user=request.user, advertisement=advertisement).first() 
        
        if not user_favored:
            new_favorite = Favorite(user=request.user, advertisement=advertisement)
            new_favorite.save()
        else:

            user_favored.delete()

        return redirect("advertisements:advertisement_details_view", advertisement_id=advertisement.id)
    except Exception as e:
        return redirect("main:home_page")
    

def favorite(request: HttpRequest):

    favorites = Favorite.objects.filter(user=request.user)

    return render(request, 'accounts/favorite.html', {"favorites" : favorites})


def validation_user_view(request: HttpRequest):
    msg =None
    pre_validation = None
    
    if request.method=="POST":

        try:
            pre_validation = Validation.objects.filter(user=request.user).first()
            if not pre_validation:
                validation = Validation (
                user =request.user, 
                national_id =request.POST["national_id"],
                id_image= request.FILES["id_image"],
                validated = request.POST["validated"],
                )
                validation.save()
                return redirect( "accounts:success_page")
            else:
                msg = "You have a previous application"
        except IntegrityError as e:
            msg = f"something went wrong {e}"
    return render(request, 'accounts/validation.html', {"msg":msg})


def success_page (request: HttpRequest):

    return render(request, 'accounts/success_page.html')

def advertisement_user(request: HttpRequest):
    user = request.user  
    advertisements = user.advertisement_set.all() 
    context = {'advertisements': advertisements} 
    return render(request, 'accounts/advertisement_user.html', context)
