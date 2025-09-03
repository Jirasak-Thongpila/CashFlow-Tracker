from django import forms
from django.forms.widgets import DateInput
from .models import Transaction
from categories.models import Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'description', 'amount', 'date', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_transaction_type'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_category'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'รายละเอียดธุรกรรม'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'หมายเหตุเพิ่มเติม (ไม่บังคับ)'
            }),
        }
        labels = {
            'transaction_type': 'ประเภทธุรกรรม',
            'category': 'หมวดหมู่',
            'description': 'รายละเอียด',
            'amount': 'จำนวนเงิน (บาท)',
            'date': 'วันที่',
            'notes': 'หมายเหตุ',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        
        # If editing, set initial transaction type and filter categories
        if self.instance and self.instance.pk:
            # Pre-populate categories based on existing transaction type
            transaction_type = self.instance.transaction_type
            if user:
                self.fields['category'].queryset = Category.objects.filter(
                    user=user,
                    category_type=transaction_type
                )
        else:
            # For new transactions, show empty category initially
            if user:
                self.fields['category'].queryset = Category.objects.filter(user=user)
            
        # Add empty option for category
        self.fields['category'].empty_label = "เลือกหมวดหมู่"
        
        # Customize transaction type field
        self.fields['transaction_type'].empty_label = "เลือกประเภท"
        
        # Make notes optional in UI
        self.fields['notes'].required = False

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        amount = cleaned_data.get('amount')

        # Validate category matches transaction type
        if transaction_type and category:
            if category.category_type != transaction_type:
                raise forms.ValidationError({
                    'category': f'หมวดหมู่ที่เลือกเป็นประเภท {category.get_category_type_display()} '
                              f'ไม่ตรงกับประเภทธุรกรรม {dict(Transaction.TRANSACTION_TYPES)[transaction_type]}'
                })

        # Validate category belongs to user
        if category and self.user and category.user != self.user:
            raise forms.ValidationError({
                'category': 'ไม่สามารถใช้หมวดหมู่ของผู้ใช้อื่นได้'
            })

        # Validate amount
        if amount and amount <= 0:
            raise forms.ValidationError({
                'amount': 'จำนวนเงินต้องมากกว่า 0'
            })

        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=False)
        if self.user:
            transaction.user = self.user
        if commit:
            transaction.save()
        return transaction


class TransactionFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ('', 'ทั้งหมด'),
        ('today', 'วันนี้'),
        ('week', '7 วันที่ผ่านมา'),
        ('month', 'เดือนนี้'),
        ('year', 'ปีนี้'),
        ('custom', 'กำหนดเอง'),
    ]
    
    transaction_type = forms.ChoiceField(
        choices=[('', 'ทุกประเภท')] + Transaction.TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label='ทุกหมวดหมู่',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ค้นหารายละเอียดหรือหมายเหตุ...'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user).order_by('category_type', 'name')