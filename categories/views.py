from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category
from .forms import CategoryForm, CategoryFilterForm

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    filter_form = CategoryFilterForm(request.GET)
    
    # Apply filters
    if filter_form.is_valid():
        category_type = filter_form.cleaned_data.get('category_type')
        search = filter_form.cleaned_data.get('search')
        
        if category_type:
            categories = categories.filter(category_type=category_type)
        
        if search:
            categories = categories.filter(
                Q(name__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(categories, 12)  # 12 categories per page
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'filter_form': filter_form,
        'income_count': Category.objects.filter(user=request.user, category_type='income').count(),
        'expense_count': Category.objects.filter(user=request.user, category_type='expense').count(),
    }
    
    return render(request, 'categories/category_list.html', context)

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'สร้างหมวดหมู่ "{category.name}" เรียบร้อยแล้ว')
            return redirect('category_list')
    else:
        form = CategoryForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'สร้างหมวดหมู่ใหม่'
    }
    return render(request, 'categories/category_form.html', context)

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขหมวดหมู่ "{category.name}" เรียบร้อยแล้ว')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category, user=request.user)
    
    context = {
        'form': form,
        'category': category,
        'title': f'แก้ไขหมวดหมู่ "{category.name}"'
    }
    return render(request, 'categories/category_form.html', context)

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'ลบหมวดหมู่ "{category_name}" เรียบร้อยแล้ว')
        return redirect('category_list')
    
    context = {
        'category': category
    }
    return render(request, 'categories/category_confirm_delete.html', context)

@login_required
def category_api_list(request):
    """API endpoint for getting categories (useful for AJAX calls)"""
    category_type = request.GET.get('type', '')
    categories = Category.objects.filter(user=request.user)
    
    if category_type in ['income', 'expense']:
        categories = categories.filter(category_type=category_type)
    
    data = []
    for category in categories:
        data.append({
            'id': category.id,
            'name': category.name,
            'display_name': category.display_name,
            'icon': category.icon,
            'color': category.color,
            'type': category.category_type,
        })
    
    return JsonResponse({'categories': data})
