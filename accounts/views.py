from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q
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
    from transactions.models import Transaction
    from categories.models import Category
    
    # Get current date and calculate date ranges
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year = today.year
    
    # Get user's transactions
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate total income and expenses
    totals = transactions.aggregate(
        total_income=Sum('amount', filter=Q(transaction_type='income')) or 0,
        total_expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
    )
    
    total_income = totals['total_income'] or 0
    total_expenses = totals['total_expenses'] or 0
    net_balance = total_income - total_expenses
    
    # Calculate current month balance
    current_month_transactions = transactions.filter(date__gte=current_month_start)
    current_month_totals = current_month_transactions.aggregate(
        month_income=Sum('amount', filter=Q(transaction_type='income')) or 0,
        month_expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
    )
    
    current_month_balance = (current_month_totals['month_income'] or 0) - (current_month_totals['month_expenses'] or 0)
    
    # Get recent transactions (last 5)
    recent_transactions = transactions.order_by('-date', '-created_at')[:5]
    
    # Generate monthly data for the current year
    monthly_labels = []
    monthly_income = []
    monthly_expenses = []
    
    for month in range(1, 13):
        month_name = datetime(current_year, month, 1).strftime('%b')
        monthly_labels.append(month_name)
        
        month_transactions = transactions.filter(date__year=current_year, date__month=month)
        month_totals = month_transactions.aggregate(
            income=Sum('amount', filter=Q(transaction_type='income')) or 0,
            expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
        )
        
        monthly_income.append(float(month_totals['income'] or 0))
        monthly_expenses.append(float(month_totals['expenses'] or 0))
    
    # Generate expense categories data for pie chart
    expense_categories_data = transactions.filter(transaction_type='expense').values(
        'category__name', 'category__color', 'category__icon'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]  # Top 10 expense categories
    
    if expense_categories_data:
        category_labels = []
        category_amounts = []
        category_colors = []
        
        for category in expense_categories_data:
            category_labels.append(f"{category['category__icon']} {category['category__name']}")
            category_amounts.append(float(category['total']))
            category_colors.append(category['category__color'])
        
        expense_categories = {
            'labels': category_labels,
            'data': category_amounts,
            'colors': category_colors
        }
    else:
        expense_categories = {
            'labels': ['ยังไม่มีข้อมูล'],
            'data': [1],
            'colors': ['#e3e6f0']
        }
    
    # Additional stats
    stats = {
        'total_transactions': transactions.count(),
        'income_transactions': transactions.filter(transaction_type='income').count(),
        'expense_transactions': transactions.filter(transaction_type='expense').count(),
        'categories_used': transactions.values('category').distinct().count(),
    }
    
    context = {
        'user': request.user,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'current_month_balance': current_month_balance,
        'recent_transactions': recent_transactions,
        'stats': stats,
        'monthly_data': {
            'labels': monthly_labels,
            'income_data': monthly_income,
            'expense_data': monthly_expenses
        },
        'expense_categories': expense_categories
    }
    
    return render(request, 'dashboard.html', context)
