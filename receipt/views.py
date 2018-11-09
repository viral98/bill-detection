import io
import os
import re
import sys
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .forms import 	UserForm, ReceiptForm
from .models import Receipt
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from receipt.tess import *
from django.utils import timezone

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'receipt/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'receipt/index.html')
            else:
                return render(request, 'receipt/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'receipt/login.html', {'error_message': 'Invalid login'})
    return render(request, 'receipt/index.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'receipt/index.html')
    context = {
        "form": form,
    }
    return render(request, 'receipt/register.html', context)


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'receipt/login.html')
    else:
        receipt = Receipt.objects.filter(user=request.user)
        query = request.GET.get("q")
        if not query:
            return render(request, 'receipt/index.html',{'receipt': receipt})


def upload_receipt(request):
    if not request.user.is_authenticated:
        return render(request, 'receipt/login.html')
    else:
        form = ReceiptForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            receipt = form.save(commit=False)	
            receipt.user = request.user
            receipt.receipt_picture = request.FILES['receipt_picture']
            file_type = receipt.receipt_picture.url.split('.')[-1]
            file_type = file_type.lower()
            rec = Receipt.objects.filter(user=request.user)
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'receipt': receipt,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'receipt/upload_receipt.html', context)
            receipt.save()
            return render(request, 'receipt/index.html',{'receipt': rec})
        context = {
            "form": form,
        }
        return render(request, 'receipt/upload_receipt.html', context)


def detail(request, receipt_id):
    if not request.user.is_authenticated:
        return render(request, 'receipt/login.html')
    else:
        user = request.user
        receipt = get_object_or_404(Receipt, pk=receipt_id)
        op = ocr(receipt.receipt_picture.url)
        from .parse import parse
        par = parse()
        print(par)
        import datetime
        if par[0] is None and par[1] is not None and par[2] is not None:
            par[0]=timezone.now()
        elif par[0] is None and par[1] is not None and par[2] is None:
            par[0]=timezone.now()
            par[2]="None"
        elif par[1] is None and par[0] is not None and par[2] is None:
            par[2]="None"    
            par[1]="None"
            par[0]=par[0].replace(" ","")
            par[0]=par[0].replace("/","-")
            par[0]=par[0].replace(".","-")
            mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
            if mat is not None:
                par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
            else:
                par[0]=timezone.now()
        elif par[1] is None and par[0] is not None and par[2] is not None:    
            par[1]="None"
            par[0]=par[0].replace(" ","")
            par[0]=par[0].replace("/","-")
            par[0]=par[0].replace(".","-")
            mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
            if mat is not None:
                par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
            else:
                par[0]=timezone.now()
        elif par[0] is None and par[1] is None and par[2] is None:
            par[0] = timezone.now()
            par[1] = "None"    
            par[2] = "None"
        elif par[0] is None and par[1] is None and par[2] is not None:
            par[0] = timezone.now()
            par[1] = "None"    
        elif par[0] is not None and par[1] is not None and par[2] is not None:    
            par[0]=par[0].replace(" ","")
            par[0]=par[0].replace("/","-")
            par[0]=par[0].replace(".","-")
            mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
            if mat is not None:
                try:
                    par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
                except:
                    par[0]=timezone.now()
            else:
                par[0]=timezone.now()
        elif par[0] is not None and par[1] is not None and par[2] is None:
            par[2]="None"    
            par[0]=par[0].replace(" ","")
            par[0]=par[0].replace("/","-")
            par[0]=par[0].replace(".","-")
            mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
            if mat is not None:
                par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
            else:
                par[0]=timezone.now()
        receipt.date = par[0]
        receipt.total = par[1]
        receipt.tax = par[2]
        receipt.save()
        return render(request, 'receipt/detail.html', {'receipt': receipt, 'user': user})


def update_ocr(request, receipt_id):
    if request.method == "POST":
        t_file = request.POST['update']
    user = request.user
    receipt = get_object_or_404(Receipt, pk=receipt_id)
    orig_stdout = sys.stdout
    f = open('receipt/media/txt/output1.txt', 'w+')
    sys.stdout = f
    print(t_file)
    sys.stdout = orig_stdout
    f.close()
    from .parse import parse
    par = parse()
    print(par)
    import datetime
    if par[0] is None and par[1] is not None and par[2] is not None:
        par[0]=timezone.now()
    elif par[0] is None and par[1] is not None and par[2] is None:
        par[0]=timezone.now()
        par[2]="None"
    elif par[1] is None and par[0] is not None and par[2] is None:
        par[2]="None"    
        par[1]="None"
        par[0]=par[0].replace(" ","")
        par[0]=par[0].replace("/","-")
        par[0]=par[0].replace(".","-")
        mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
        if mat is not None:
            par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            par[0]=timezone.now()
    elif par[1] is None and par[0] is not None and par[2] is not None:    
        par[1]="None"
        par[0]=par[0].replace(" ","")
        par[0]=par[0].replace("/","-")
        par[0]=par[0].replace(".","-")
        mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
        if mat is not None:
            par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            par[0]=timezone.now()
    elif par[0] is None and par[1] is None and par[2] is None:
        par[0] = timezone.now()
        par[1] = "None"    
        par[2] = "None"
    elif par[0] is None and par[1] is None and par[2] is not None:
        par[0] = timezone.now()
        par[1] = "None"    
    elif par[0] is not None and par[1] is not None and par[2] is not None:    
        par[0]=par[0].replace(" ","")
        par[0]=par[0].replace("/","-")
        par[0]=par[0].replace(".","-")
        mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
        if mat is not None:
            par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            par[0]=timezone.now()
    elif par[0] is not None and par[1] is not None and par[2] is None:
        par[2]="None"    
        par[0]=par[0].replace(" ","")
        par[0]=par[0].replace("/","-")
        par[0]=par[0].replace(".","-")
        mat=re.match('\d{1,2}-\d{1,2}-\d{2,4}', par[0])
        if mat is not None:
            par[0]=datetime.datetime.strptime(par[0],'%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            par[0]=timezone.now()
    receipt.date = par[0]
    receipt.total = par[1]
    receipt.tax = par[2]
    receipt.save()

    return render(request, 'receipt/detail.html', {'receipt': receipt, 'user': user})
