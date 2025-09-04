from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Transaction
from .forms import TransactionForm, TransactionFilterForm
from categories.models import Category

@login_required
def transaction_list(request):
    transactions = Transaction.objects.for_user(request.user)
    filter_form = TransactionFilterForm(request.GET, user=request.user)
    
    # Apply filters
    if filter_form.is_valid():
        transaction_type = filter_form.cleaned_data.get('transaction_type')
        category = filter_form.cleaned_data.get('category')
        period = filter_form.cleaned_data.get('period')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        search = filter_form.cleaned_data.get('search')
        
        if transaction_type == 'income':
            transactions = transactions.income()
        elif transaction_type == 'expense':
            transactions = transactions.expenses()
        
        if category:
            transactions = transactions.for_category(category)
        
        if search:
            transactions = transactions.search(search)
        
        # Handle period filters
        today = timezone.now().date()
        if period == 'today':
            transactions = transactions.for_period(start_date=today, end_date=today)
        elif period == 'week':
            week_ago = today - timedelta(days=7)
            transactions = transactions.for_period(start_date=week_ago)
        elif period == 'month':
            month_start = today.replace(day=1)
            transactions = transactions.for_period(start_date=month_start)
        elif period == 'year':
            year_start = today.replace(month=1, day=1)
            transactions = transactions.for_period(start_date=year_start)
        elif period == 'custom':
            transactions = transactions.for_period(start_date=date_from, end_date=date_to)
    
    # Calculate statistics using optimized method
    stats = transactions.totals_summary()
    stats['net_balance'] = (stats['total_income'] or 0) - (stats['total_expense'] or 0)
    stats['transaction_count'] = transactions.count()
    
    # Optimized pagination with better error handling
    paginator = Paginator(transactions, 20)  # 20 transactions per page
    page_number = request.GET.get('page', 1)
    
    try:
        transactions = paginator.page(page_number)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    
    context = {
        'transactions': transactions,
        'filter_form': filter_form,
        'stats': stats,
    }
    
    return render(request, 'transactions/transaction_list.html', context)

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, f'เพิ่มรายการ "{transaction.description}" เรียบร้อยแล้ว')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'เพิ่มรายการใหม่'
    }
    return render(request, 'transactions/transaction_form.html', context)

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขรายการ "{transaction.description}" เรียบร้อยแล้ว')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    context = {
        'form': form,
        'transaction': transaction,
        'title': f'แก้ไขรายการ "{transaction.description}"'
    }
    return render(request, 'transactions/transaction_form.html', context)

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction_desc = transaction.description
        transaction.delete()
        messages.success(request, f'ลบรายการ "{transaction_desc}" เรียบร้อยแล้ว')
        return redirect('transaction_list')
    
    context = {
        'transaction': transaction
    }
    return render(request, 'transactions/transaction_confirm_delete.html', context)

@login_required
def get_categories_by_type(request):
    """API endpoint to get categories filtered by transaction type"""
    transaction_type = request.GET.get('type', '')
    
    if transaction_type == 'income':
        categories = Category.objects.for_user(request.user).income_categories().order_by('name')
    elif transaction_type == 'expense':
        categories = Category.objects.for_user(request.user).expense_categories().order_by('name')
    else:
        return JsonResponse({'categories': []})
        
    data = []
    for category in categories:
        data.append({
            'id': category.id,
            'name': category.name,
            'display_name': category.display_name,
            'icon': category.icon,
            'color': category.color,
        })
    
    return JsonResponse({'categories': data})
