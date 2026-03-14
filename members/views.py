from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from . forms import CustomUserCreationForm


def logout_user(request):
    #logout the user that issues the request
    logout(request)
    #Display message that loggout is a success
    messages.success(request,("You have logged out"))
    #redirect to landing page
    return redirect('welcome')

def register_user(request):
    #if the form has been submitted
    if request.method == "POST":
        #make a CustomUserCreationForm
        form = CustomUserCreationForm(request.POST)
        #if the form is valid
        if form.is_valid():
            #save it
            form.save()
            #authentiate and login the new registered user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password = password)
            login(request, user)
            messages.success(request, ("You have joined!"))
            #redirect to the landing page
            return redirect('welcome')
    else:
        #present and empty form
        form = CustomUserCreationForm()
    #render the register page
    return render(request, 'members/register_user.html', {'form': form})