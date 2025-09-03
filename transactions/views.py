from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Transaction
from .forms import TransactionForm, TransactionFilterForm
from categories.models import Category

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    filter_form = TransactionFilterForm(request.GET, user=request.user)
    
    # Apply filters
    if filter_form.is_valid():
        transaction_type = filter_form.cleaned_data.get('transaction_type')
        category = filter_form.cleaned_data.get('category')
        period = filter_form.cleaned_data.get('period')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        search = filter_form.cleaned_data.get('search')
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        if category:
            transactions = transactions.filter(category=category)
        
        if search:
            transactions = transactions.filter(
                Q(description__icontains=search) | Q(notes__icontains=search)
            )
        
        # Handle period filters
        today = timezone.now().date()
        if period == 'today':
            transactions = transactions.filter(date=today)
        elif period == 'week':
            week_ago = today - timedelta(days=7)
            transactions = transactions.filter(date__gte=week_ago)
        elif period == 'month':
            transactions = transactions.filter(date__year=today.year, date__month=today.month)
        elif period == 'year':
            transactions = transactions.filter(date__year=today.year)
        elif period == 'custom':
            if date_from:
                transactions = transactions.filter(date__gte=date_from)
            if date_to:
                transactions = transactions.filter(date__lte=date_to)
    
    # Calculate statistics
    stats = transactions.aggregate(
        total_income=Sum('amount', filter=Q(transaction_type='income')) or 0,
        total_expense=Sum('amount', filter=Q(transaction_type='expense')) or 0
    )
    
    stats['net_balance'] = (stats['total_income'] or 0) - (stats['total_expense'] or 0)
    stats['transaction_count'] = transactions.count()
    
    # Pagination
    paginator = Paginator(transactions, 20)  # 20 transactions per page
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
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
    
    if transaction_type in ['income', 'expense']:
        categories = Category.objects.filter(
            user=request.user,
            category_type=transaction_type
        ).order_by('name')
        
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
    
    return JsonResponse({'categories': []})
