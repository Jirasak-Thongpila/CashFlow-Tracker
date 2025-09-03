from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'รายรับ'),
        ('expense', 'รายจ่าย'),
    ]
    
    COLOR_CHOICES = [
        ('#FF6B6B', 'แดง'),
        ('#4ECDC4', 'เขียวน้ำทะเล'),
        ('#45B7D1', 'ฟ้า'),
        ('#96CEB4', 'เขียวอ่อน'),
        ('#FECA57', 'เหลือง'),
        ('#FF9FF3', 'ชมพู'),
        ('#54A0FF', 'น้ำเงิน'),
        ('#5F27CD', 'ม่วง'),
        ('#00D2D3', 'ฟ้าใส'),
        ('#FF9F43', 'ส้ม'),
        ('#10AC84', 'เขียว'),
        ('#EE5A24', 'ส้มแดง'),
        ('#0ABDE3', 'ฟ้าอ่อน'),
        ('#C44569', 'แดงอ่อน'),
        ('#40739E', 'น้ำเงินเข้ม'),
    ]
    
    ICON_CHOICES = [
        ('💰', 'เงิน'),
        ('🏠', 'บ้าน'),
        ('🍕', 'อาหาร'),
        ('⛽', 'น้ำมัน'),
        ('🚗', 'รถยนต์'),
        ('🎬', 'ความบันเทิง'),
        ('👕', 'เสื้อผ้า'),
        ('💊', 'สุขภาพ'),
        ('📚', 'การศึกษา'),
        ('💼', 'ธุรกิจ'),
        ('🎁', 'ของขวัญ'),
        ('✈️', 'การเดินทาง'),
        ('📱', 'เทคโนโลยี'),
        ('🏦', 'ธนาคาร'),
        ('💳', 'บัตรเครดิต'),
        ('🛍️', 'ช้อปปิ้ง'),
        ('🏥', 'โรงพยาบาล'),
        ('🎵', 'ดนตรี'),
        ('⚡', 'สาธารณูปโภค'),
        ('🍽️', 'ร้านอาหาร'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, verbose_name='ชื่อหมวดหมู่')
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, verbose_name='ประเภท')
    icon = models.CharField(max_length=10, choices=ICON_CHOICES, default='💰', verbose_name='ไอคอน')
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#FF6B6B', verbose_name='สี')
    is_default = models.BooleanField(default=False, verbose_name='หมวดหมู่เริ่มต้น')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่แก้ไขล่าสุด')
    
    class Meta:
        verbose_name = 'หมวดหมู่'
        verbose_name_plural = 'หมวดหมู่'
        ordering = ['category_type', 'name']
        unique_together = ['user', 'name', 'category_type']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"
    
    @property
    def display_name(self):
        return f"{self.icon} {self.name}"
