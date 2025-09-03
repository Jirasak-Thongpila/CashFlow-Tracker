from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user', 'icon', 'color', 'is_default', 'created_at']
    list_filter = ['category_type', 'is_default', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    ordering = ['category_type', 'name']
