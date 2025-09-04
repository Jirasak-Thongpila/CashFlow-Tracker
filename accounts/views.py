from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .forms import CustomUserCreationForm

def get_dashboard_stats(user, cache_key_suffix=""):
    """Get cached dashboard statistics for a user"""
    cache_key = f"dashboard_stats_{user.id}_{cache_key_suffix}"
    stats = cache.get(cache_key)
    
    if stats is None:
        from transactions.models import Transaction
        
        # Get user's transactions with optimized queries
        transactions = Transaction.objects.for_user(user)
        
        # Calculate total income and expenses using optimized manager method
        totals = transactions.totals_summary()
        
        total_income = totals['total_income'] or 0
        total_expenses = totals['total_expenses'] or 0
        net_balance = total_income - total_expenses
        
        # Calculate current month balance
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        current_month_transactions = transactions.for_period(start_date=current_month_start)
        current_month_totals = current_month_transactions.totals_summary()
        current_month_balance = (current_month_totals['total_income'] or 0) - (current_month_totals['total_expenses'] or 0)
        
        # Additional stats
        additional_stats = {
            'total_transactions': transactions.count(),
            'income_transactions': transactions.income().count(),
            'expense_transactions': transactions.expenses().count(),
            'categories_used': transactions.values('category').distinct().count(),
        }
        
        stats = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'current_month_balance': current_month_balance,
            'stats': additional_stats,
            'transactions_queryset': transactions,  # For other calculations
        }
        
        # Cache for 5 minutes by default
        cache.set(cache_key, stats, getattr(settings, 'CACHE_TTL', 300))
    
    return stats

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
    current_year = today.year
    
    # Get cached dashboard statistics
    cached_stats = get_dashboard_stats(request.user, f"dashboard_{today.strftime('%Y%m%d')}")
    transactions = cached_stats['transactions_queryset']
    
    # Get recent transactions (last 5)
    recent_transactions = transactions.order_by('-date', '-created_at')[:5]
    
    # Generate monthly data for the current year
    monthly_labels = []
    monthly_income = []
    monthly_expenses = []
    
    for month in range(1, 13):
        month_name = datetime(current_year, month, 1).strftime('%b')
        monthly_labels.append(month_name)
        
        month_start = datetime(current_year, month, 1).date()
        if month < 12:
            month_end = datetime(current_year, month + 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(current_year, 12, 31).date()
        
        month_transactions = transactions.for_period(start_date=month_start, end_date=month_end)
        month_totals = month_transactions.totals_summary()
        
        monthly_income.append(float(month_totals['total_income'] or 0))
        monthly_expenses.append(float(month_totals['total_expenses'] or 0))
    
    # Generate expense categories data for pie chart
    expense_categories_data = transactions.expenses().values(
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
    
    # Use cached stats
    stats = cached_stats['stats']
    
    context = {
        'user': request.user,
        'total_income': cached_stats['total_income'],
        'total_expenses': cached_stats['total_expenses'],
        'net_balance': cached_stats['net_balance'],
        'current_month_balance': cached_stats['current_month_balance'],
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

@login_required
def get_cashflow_data(request):
    """API endpoint for dynamic cash flow chart data"""
    from transactions.models import Transaction
    from django.http import JsonResponse
    
    # Get parameters
    period = request.GET.get('period', 'year')  # year, 6months, 3months, month, week
    year = request.GET.get('year', timezone.now().year)
    
    try:
        year = int(year)
    except (ValueError, TypeError):
        year = timezone.now().year
    
    today = timezone.now().date()
    transactions = Transaction.objects.for_user(request.user)
    
    labels = []
    income_data = []
    expense_data = []
    net_flow_data = []
    running_balance_data = []
    
    running_balance = 0
    
    if period == 'year':
        # Monthly data for the specified year
        for month in range(1, 13):
            month_name = datetime(year, month, 1).strftime('%b %Y')
            labels.append(month_name)
            
            month_transactions = transactions.filter(date__year=year, date__month=month)
            month_totals = month_transactions.aggregate(
                income=Sum('amount', filter=Q(transaction_type='income')) or 0,
                expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
            )
            
            income = float(month_totals['income'] or 0)
            expenses = float(month_totals['expenses'] or 0)
            net_flow = income - expenses
            running_balance += net_flow
            
            income_data.append(income)
            expense_data.append(expenses)
            net_flow_data.append(net_flow)
            running_balance_data.append(running_balance)
    
    elif period == '6months':
        # Last 6 months
        start_date = today.replace(day=1) - timedelta(days=150)  # Approximate
        for i in range(6):
            month_date = start_date + timedelta(days=30*i)
            month_name = month_date.strftime('%b %Y')
            labels.append(month_name)
            
            month_transactions = transactions.filter(
                date__year=month_date.year, 
                date__month=month_date.month
            )
            month_totals = month_transactions.aggregate(
                income=Sum('amount', filter=Q(transaction_type='income')) or 0,
                expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
            )
            
            income = float(month_totals['income'] or 0)
            expenses = float(month_totals['expenses'] or 0)
            net_flow = income - expenses
            running_balance += net_flow
            
            income_data.append(income)
            expense_data.append(expenses)
            net_flow_data.append(net_flow)
            running_balance_data.append(running_balance)
    
    elif period == '3months':
        # Last 3 months
        for i in range(3):
            month_date = (today.replace(day=1) - timedelta(days=32*i))
            month_name = month_date.strftime('%b %Y')
            labels.insert(0, month_name)
            
            month_transactions = transactions.filter(
                date__year=month_date.year, 
                date__month=month_date.month
            )
            month_totals = month_transactions.aggregate(
                income=Sum('amount', filter=Q(transaction_type='income')) or 0,
                expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
            )
            
            income = float(month_totals['income'] or 0)
            expenses = float(month_totals['expenses'] or 0)
            net_flow = income - expenses
            
            income_data.insert(0, income)
            expense_data.insert(0, expenses)
            net_flow_data.insert(0, net_flow)
        
        # Calculate running balance properly for 3 months
        running_balance = 0
        running_balance_data = []
        for net in net_flow_data:
            running_balance += net
            running_balance_data.append(running_balance)
    
    elif period == 'month':
        # Current month by weeks
        month_start = today.replace(day=1)
        weeks = []
        current_date = month_start
        
        while current_date.month == today.month:
            week_end = min(current_date + timedelta(days=6), today)
            weeks.append((current_date, week_end))
            current_date = week_end + timedelta(days=1)
        
        for i, (week_start, week_end) in enumerate(weeks):
            labels.append(f'สัปดาห์ {i+1}')
            
            week_transactions = transactions.filter(
                date__gte=week_start,
                date__lte=week_end
            )
            week_totals = week_transactions.aggregate(
                income=Sum('amount', filter=Q(transaction_type='income')) or 0,
                expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
            )
            
            income = float(week_totals['income'] or 0)
            expenses = float(week_totals['expenses'] or 0)
            net_flow = income - expenses
            running_balance += net_flow
            
            income_data.append(income)
            expense_data.append(expenses)
            net_flow_data.append(net_flow)
            running_balance_data.append(running_balance)
    
    elif period == 'week':
        # Last 7 days
        for i in range(7):
            date = today - timedelta(days=6-i)
            labels.append(date.strftime('%d %b'))
            
            day_transactions = transactions.filter(date=date)
            day_totals = day_transactions.aggregate(
                income=Sum('amount', filter=Q(transaction_type='income')) or 0,
                expenses=Sum('amount', filter=Q(transaction_type='expense')) or 0
            )
            
            income = float(day_totals['income'] or 0)
            expenses = float(day_totals['expenses'] or 0)
            net_flow = income - expenses
            running_balance += net_flow
            
            income_data.append(income)
            expense_data.append(expenses)
            net_flow_data.append(net_flow)
            running_balance_data.append(running_balance)
    
    # Calculate summary statistics
    total_income = sum(income_data)
    total_expenses = sum(expense_data)
    total_net_flow = sum(net_flow_data)
    final_balance = running_balance_data[-1] if running_balance_data else 0
    
    return JsonResponse({
        'labels': labels,
        'datasets': {
            'income': income_data,
            'expenses': expense_data,
            'net_flow': net_flow_data,
            'running_balance': running_balance_data
        },
        'summary': {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_flow': total_net_flow,
            'final_balance': final_balance,
            'period': period,
            'data_points': len(labels)
        }
    })
