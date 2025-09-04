from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from categories.models import Category
from decimal import Decimal

User = get_user_model()

class TransactionQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user).select_related('category')
    
    def income(self):
        return self.filter(transaction_type='income')
    
    def expenses(self):
        return self.filter(transaction_type='expense')
    
    def for_period(self, start_date=None, end_date=None):
        queryset = self
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset
    
    def for_category(self, category):
        return self.filter(category=category)
    
    def totals_summary(self):
        return self.aggregate(
            total_income=Sum('amount', filter=Q(transaction_type='income')) or 0,
            total_expense=Sum('amount', filter=Q(transaction_type='expense')) or 0
        )
    
    def search(self, query):
        return self.filter(
            Q(description__icontains=query) | 
            Q(notes__icontains=query)
        )

class TransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def income(self):
        return self.get_queryset().income()
    
    def expenses(self):
        return self.get_queryset().expenses()

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'รายรับ'),
        ('expense', 'รายจ่าย'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', verbose_name='ผู้ใช้')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions', verbose_name='หมวดหมู่')
    description = models.CharField(max_length=255, verbose_name='รายละเอียด')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='จำนวนเงิน')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name='ประเภท')
    date = models.DateField(verbose_name='วันที่')
    notes = models.TextField(blank=True, verbose_name='หมายเหตุ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่แก้ไขล่าสุด')
    
    objects = TransactionManager()
    
    class Meta:
        verbose_name = 'รายการธุรกรรม'
        verbose_name_plural = 'รายการธุรกรรม'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'transaction_type', 'date']),
            models.Index(fields=['user', 'category', 'date']),
            models.Index(fields=['date', 'created_at']),
            models.Index(fields=['user', 'amount']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.description} ({self.amount})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate that transaction_type matches category type
        if self.category and self.transaction_type:
            if self.category.category_type != self.transaction_type:
                raise ValidationError({
                    'category': f'หมวดหมู่ที่เลือกเป็นประเภท {self.category.get_category_type_display()} '
                              f'ไม่ตรงกับประเภทธุรกรรม {self.get_transaction_type_display()}'
                })
        
        # Validate amount is positive
        if self.amount and self.amount <= 0:
            raise ValidationError({
                'amount': 'จำนวนเงินต้องมากกว่า 0'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def signed_amount(self):
        """Returns amount with appropriate sign based on transaction type"""
        if self.transaction_type == 'income':
            return self.amount
        else:
            return -self.amount
    
    @property
    def category_display(self):
        """Returns category with icon for display"""
        if self.category:
            return f"{self.category.icon} {self.category.name}"
        return ""
