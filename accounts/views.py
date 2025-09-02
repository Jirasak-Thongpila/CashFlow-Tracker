from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to CashFlow Tracker.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get current date and calculate date ranges
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    
    # Placeholder data - will be replaced with real transaction data later
    context = {
        'user': request.user,
        'total_income': 0.00,
        'total_expenses': 0.00,
        'net_balance': 0.00,
        'current_month_balance': 0.00,
        'recent_transactions': [],
        'monthly_data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'income_data': [0, 0, 0, 0, 0, 0],
            'expense_data': [0, 0, 0, 0, 0, 0]
        },
        'expense_categories': {
            'labels': ['No data yet'],
            'data': [1],
            'colors': ['#e3e6f0']
        }
    }
    
    return render(request, 'dashboard.html', context)
