from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อหมวดหมู่'
            }),
            'category_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'icon': forms.Select(attrs={
                'class': 'form-control'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'ชื่อหมวดหมู่',
            'category_type': 'ประเภท',
            'icon': 'ไอคอน',
            'color': 'สี',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Add color preview to color choices
        color_choices = []
        for value, label in Category.COLOR_CHOICES:
            color_choices.append((value, f"{label} ({value})"))
        self.fields['color'].choices = color_choices
        
        # Add icon preview to icon choices
        icon_choices = []
        for value, label in Category.ICON_CHOICES:
            icon_choices.append((value, f"{value} {label}"))
        self.fields['icon'].choices = icon_choices

    def clean_name(self):
        name = self.cleaned_data.get('name')
        category_type = self.cleaned_data.get('category_type')
        
        # Check if category with same name and type exists for this user
        existing_category = Category.objects.filter(
            user=self.user,
            name=name,
            category_type=category_type
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if existing_category.exists():
            raise forms.ValidationError('หมวดหมู่นี้มีอยู่แล้วสำหรับประเภทนี้')
        
        return name

class CategoryFilterForm(forms.Form):
    category_type = forms.ChoiceField(
        choices=[('', 'ทั้งหมด')] + Category.CATEGORY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ค้นหาหมวดหมู่...'
        })
    )