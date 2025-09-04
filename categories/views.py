from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Category
from .forms import CategoryForm, CategoryFilterForm

@login_required
def category_list(request):
    categories = Category.objects.for_user(request.user)
    filter_form = CategoryFilterForm(request.GET)
    
    # Apply filters
    if filter_form.is_valid():
        category_type = filter_form.cleaned_data.get('category_type')
        search = filter_form.cleaned_data.get('search')
        
        if category_type == 'income':
            categories = categories.income_categories()
        elif category_type == 'expense':
            categories = categories.expense_categories()
        
        if search:
            categories = categories.filter(
                Q(name__icontains=search)
            )
    
    # Optimized pagination with better error handling
    paginator = Paginator(categories, 12)  # 12 categories per page
    page_number = request.GET.get('page', 1)
    
    try:
        categories = paginator.page(page_number)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
        'filter_form': filter_form,
        'income_count': Category.objects.for_user(request.user).income_categories().count(),
        'expense_count': Category.objects.for_user(request.user).expense_categories().count(),
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
    categories = Category.objects.for_user(request.user)
    
    if category_type == 'income':
        categories = categories.income_categories()
    elif category_type == 'expense':
        categories = categories.expense_categories()
    
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

@login_required
def category_create_ajax(request):
    """AJAX endpoint for creating categories inline"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            name = data.get('name', '').strip()
            category_type = data.get('category_type', '')
            icon = data.get('icon', '💰')
            color = data.get('color', '#FF6B6B')
            
            if not name or category_type not in ['income', 'expense']:
                return JsonResponse({
                    'success': False,
                    'error': 'กรุณาระบุชื่อหมวดหมู่และประเภทที่ถูกต้อง'
                }, status=400)
            
            # Check if category already exists
            if Category.objects.filter(user=request.user, name=name, category_type=category_type).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'หมวดหมู่นี้มีอยู่แล้ว'
                }, status=400)
            
            # Create new category
            category = Category.objects.create(
                user=request.user,
                name=name,
                category_type=category_type,
                icon=icon,
                color=color,
                is_default=False
            )
            
            return JsonResponse({
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'display_name': category.display_name,
                    'icon': category.icon,
                    'color': category.color,
                    'category_type': category.category_type,
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'ข้อมูลที่ส่งมาไม่ถูกต้อง'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'เกิดข้อผิดพลาดในการสร้างหมวดหมู่'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)
