from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'category_display', 'transaction_type', 'amount', 'user', 'created_at']
    list_filter = ['transaction_type', 'category', 'date', 'created_at']
    search_fields = ['description', 'notes', 'user__username', 'user__email', 'category__name']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('ข้อมูลหลัก', {
            'fields': ('user', 'transaction_type', 'category')
        }),
        ('รายละเอียด', {
            'fields': ('description', 'amount', 'date', 'notes')
        }),
        ('ข้อมูลระบบ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def category_display(self, obj):
        return obj.category_display
    category_display.short_description = 'หมวดหมู่'
    category_display.admin_order_field = 'category__name'
