from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Income, Expense

@login_required
def dashboard_view(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
    expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    balance = total_income - total_expense
    
    context = {
        'recent_incomes': incomes,
        'recent_expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'finance/dashboard.html', context)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'บัญชีสำหรับ {username} ถูกสร้างแล้ว!')
            login(request, user)
            return redirect('finance:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('finance:dashboard')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render(request, 'registration/login.html')

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')

@login_required
def income_list_view(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'finance/income_list.html', {'incomes': incomes})

@login_required
def income_form_view(request, pk=None):
    return render(request, 'finance/income_form.html')

@login_required
def expense_list_view(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'finance/expense_list.html', {'expenses': expenses})

@login_required
def expense_form_view(request, pk=None):
    return render(request, 'finance/expense_form.html')

@login_required
def transaction_list_view(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'finance/transaction_list.html', {
        'incomes': incomes,
        'expenses': expenses
    })
