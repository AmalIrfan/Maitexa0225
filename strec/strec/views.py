from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from .models import UserData

import json

import os
API_KEY=os.environ["API_KEY"]

def getinfo(request):
    
    return

import urllib
from urllib import request as ureq

def index(request):
    if request.method == "POST" and "delete" in request.GET:
        d = UserData.objects.get(id=request.POST["id"])
        d.delete()
        request.session["message"] = "Deleted"
        return JsonResponse({'status': 'success', 'redirect_url': '/'})
    if request.method == "POST" and "regen" in request.GET:
        # Only the last file uploaded is considered
        data = UserData.objects.filter(user=request.user)
        for d in data:
            csv = d.datafile.open("r").read()
            q = json.dumps({"contents":[{"parts":[{"text":"""The answer should be one or more job titles.
Based on given csv data of year of course, name of course, and aggregate score;
What is the person with this qualification maybe best suitable for?
-----csv start----

%s""" % csv}]}]})
        if q:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=%s" % API_KEY
            req = ureq.Request(url, data=q.encode("utf-8"))
            req.add_header('Content-Type', 'application/json')
            resp = ureq.urlopen(req).read()
            resp = '{\n  "candidates": [\n    {\n      "content": {\n        "parts": [\n          {\n            "text": "Chemical Laboratory Technician,  Chemistry Technician,  Lab Assistant\\n"\n          }\n        ],\n        "role": "model"\n      },\n      "finishReason": "STOP",\n      "avgLogprobs": -0.52077798048655188\n    }\n  ],\n  "usageMetadata": {\n    "promptTokenCount": 113,\n    "candidatesTokenCount": 12,\n    "totalTokenCount": 125,\n    "promptTokensDetails": [\n      {\n        "modality": "TEXT",\n        "tokenCount": 113\n      }\n    ],\n    "candidatesTokensDetails": [\n      {\n        "modality": "TEXT",\n        "tokenCount": 12\n      }\n    ]\n  },\n  "modelVersion": "gemini-1.5-flash"\n}\n'
            print(resp)
            datas = json.loads(resp)["candidates"][0]["content"]["parts"][0]["text"].strip().split(",")
            request.session["suggestions"] = datas
            request.session["message"] = "Regenerated."
            return JsonResponse({'status': 'success', 'redirect_url': '/'})
        else:
            return JsonResponse({'status': 'failse', 'message': 'Error'})
    if request.method == "POST":
        (UserData.objects
        .create(user=request.user, datafile=request.FILES["file"])
        .save())
        if 1:
            request.session["message"] = "Uploaded"
            return JsonResponse({'status': 'success', 'redirect_url': '/'})
        else:
            return JsonResponse({'status': 'failed', 'message':'Invalid input.'})
    data=None
    if request.user.is_authenticated:
        data = UserData.objects.filter(user=request.user)

    message = ""
    if "message" in request.session:
        message = request.session["message"]
        del request.session["message"]
    return render(request, "index.html", {"data":data,"message":message, })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        form = AuthenticationForm()
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            request.session["message"] = 'Logged in.'
            return JsonResponse({'status': 'success', 'redirect_url': '/'})
        else:
            return JsonResponse({'status': 'failed', 'message':'Invalid input.'})
    return render(request, "login.html")

def logout_view(request):
    request.session["message"] = 'Logged out.'
    if request.user.is_authenticated:
        logout(request)
        request.session["message"] = 'Successfully logged out.'
    return redirect('/')

def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            login(request, user)
            request.session["message"] = 'Signup successful.'
            return JsonResponse({'status': 'success', 'redirect_url': '/'})
        except:
            return JsonResponse({'status': 'failed', 'message':'Invalid Input.'})
    return render(request, "signup.html")


def delete_account(request):
    request.session["message"] = 'Not logged in.'
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        User.objects.get(username=username).delete()
        request.session["message"] = 'Account deleted.'
    return redirect("/")