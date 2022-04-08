from contextvars import Context
from datetime import datetime
import email
from email.message import EmailMessage
import imp
from random import randint
from django.http import HttpResponse
from django.core.mail import send_mail
import math, random
import random
from time import time
from ticketsys import settings
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.contrib import messages
import mysql.connector as sql
from django.views.decorators.csrf import csrf_exempt
from account.models import Ticketgeneration,UserOTP
from django.template import Context
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string,get_template
from django.utils.html import strip_tags

# Create your views here.

def home(request):
    user = request.user
    ticketdata = Ticketgeneration.objects.filter(username = user)
    return render(request, 'account/index.html',{'ticketdata': ticketdata})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request,user)
            email = request.user

            #Welcome mail
            subject = "Loged-In in Local Train Ticket system"
            message = "Hello" + user.username + "!!\n" + "We found that you have recently login in.\n" + "We hope its you. If not please change your Password on the given link" + ":" + "http://127.0.0.1:8000/password_reset/"
            from_email= settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject,message,from_email,to_list,fail_silently=False)

            # html_content = render_to_string("account/tickettemp.html",{'name':user.username})
            # text_content = strip_tags(html_content)

            # email = EmailMultiAlternatives(
            #     "WELCOME TO TICKETSYSTEM",text_content,'localticketsystem2022@gmail.com',[email]
            # )

            # email.attach_alternative(html_content,'text/html')
            # email.send()
            # template = render_to_string('account/welcometemp.html',{'name':user.username})
            # emailmsg = EmailMultiAlternatives(
            #     'Welcome to Ticket SYStem',
            #     template,
            #     settings.EMAIL_HOST_USER,
            #     [user.email],
            # )
            # emailmsg.attach_alternative(template,'text/html')
            # emailmsg.fail_silently=False
            # emailmsg.send()
            
            return redirect('home')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')

    else:
        return render(request, 'account/signin.html')

def register(request):

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if(password1 == password2):
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name,last_name=last_name)
                user.save()
                print('User Created')
                get_otp = request.POST.get('otp') #213243 #None

                if get_otp:
                    get_usr = request.POST.get('usr')
                    user = User.objects.get(username=get_usr)
                    if int(get_otp) == UserOTP.objects.filter(user = user).last().otp:
                        user.is_active = True
                        user.save()
                        messages.success(request, f'Account is Created For {user.username}')
                        return redirect('login')
                    else:
                        messages.warning(request, f'You Entered a Wrong OTP')
                        return render(request, 'account/signup.html', {'otp': True, 'usr': user})
        
                #Welcome message
                template = render_to_string('account/welcometemp.html',{'name':user.username})
                emailmsg = EmailMultiAlternatives(
                    'Welcome to Ticket SYStem',
                    template,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                emailmsg.attach_alternative(template,'text/html')
                emailmsg.fail_silently=False
                emailmsg.send()
                return redirect('login')

        else:
            messages.info(request,'Password not matching')
            return redirect('register')
        return redirect('home')


    else:
        return render(request, 'account/signup.html')


def logout(request):
    auth.logout(request)
    return redirect('home')


def ticket(request):
    if request.method == 'POST':
        ticketid = request.POST.get("ticketid")
        email = request.POST['email']
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        username = request.POST.get('username')
        checkbox = request.POST.get('checkbox')
        adult = request.POST.get('adult')
        from_station = request.POST.get('from')
        to = request.POST.get('to')
        rate = request.POST.get('rate')
        date = request.POST.get('date')
        usermessage = request.POST.get('usermessage')
        return render(request, 'account/ticketconf.html',{"ticketid":ticketid,"email":email, "fname":fname, "lname":lname, "username":username, "checkbox":checkbox, "adult":adult, "from_station":from_station, "to":to, "rate":rate, "date":date , "usermessage": usermessage})
    else:
        return render(request, 'account/ticket.html')


def ticketconf(request):
    user = request.user
    if request.method == 'POST':
        ticketid = str(random.randint(100000000, 999999999))
        email = request.POST['email']
        username = request.POST.get('username')
        checkbox = request.POST['checkbox']
        adult = request.POST['adult']
        fromstation = request.POST['fromstation']
        tostation = request.POST['tostation']
        rate = request.POST["rate"]
        usermessage = request.POST['usermessage']
        date = request.POST['ticketdate']
        #date = datetime.date.today()
        time = request.POST['time']

        
        ticketgeneration = Ticketgeneration(ticketid=ticketid,email=email,username=username,checkbox=checkbox,adult=adult,fromstation=fromstation,tostation=tostation,rate=rate,date=date,usermessage=usermessage,time=time)
        ticketgeneration.save()

        template = render_to_string('account/tickettemp.html', {'ticketid':ticketid,'checkbox':checkbox,'adult':adult,'fromstation':fromstation,'tostation':tostation,'date':date,'rate':rate,'usermessage':usermessage,'time':time})
        emailmsg = EmailMultiAlternatives(
            'Welcome to Ticket SYStem',
            template,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        emailmsg.attach_alternative(template,'text/html')
        emailmsg.fail_silently=False
        emailmsg.send()   

        return render(request, 'account/tickettemp.html',{'ticketid':ticketid,'checkbox':checkbox,'adult':adult,'fromstation':fromstation,'tostation':tostation,'date':date,'rate':rate,'usermessage':usermessage,'time':time})


    else:
        return render(request, 'account/ticket.html')


def tickettemp(request):
    html_content = render_to_string("account/tickettemp.html",{'title':'E-Ticket'})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        "Ticket",text_content,settings.EMAIL_HOST_USER,[email]
    )

    email.attach_alternative(html_content,'text/html')
    email.send()

    return render(request, 'account/tickettemp.html')


def viewticket(request,pk):
    ticketdata = Ticketgeneration.objects.get(id=pk)
    if request.method == 'POST':
        ticketid = str(random.randint(100000000, 999999999))
        email = request.POST['email']
        username = request.POST.get('username')
        checkbox = request.POST['checkbox']
        adult = request.POST['adult']
        fromstation = request.POST['fromstation']
        tostation = request.POST['tostation']
        rate = request.POST["rate"]
        usermessage = request.POST['usermessage']
        date = request.POST['ticketdate']
        #date = datetime.date.today()
        time = request.POST['time']

        
        ticketgeneration = Ticketgeneration(ticketid=ticketid,email=email,username=username,checkbox=checkbox,adult=adult,fromstation=fromstation,tostation=tostation,rate=rate,date=date,usermessage=usermessage,time=time)
        ticketgeneration.save()
    return render(request,'account/ticketview.html',{'ticketdata':ticketdata})
