from django.db import models
from django.contrib.auth import get_user_model
from categories.models import Category
from decimal import Decimal

User = get_user_model()

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
    
    class Meta:
        verbose_name = 'รายการธุรกรรม'
        verbose_name_plural = 'รายการธุรกรรม'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
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
