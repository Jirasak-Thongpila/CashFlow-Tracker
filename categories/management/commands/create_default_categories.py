from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from categories.models import Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Create default categories for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Create categories for specific user ID only',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            users = User.objects.all()

        # Default income categories
        income_categories = [
            {'name': 'เงินเดือน', 'icon': '💰', 'color': '#28a745'},
            {'name': 'โบนัส', 'icon': '🎁', 'color': '#17a2b8'},
            {'name': 'ธุรกิจส่วนตัว', 'icon': '💼', 'color': '#6f42c1'},
            {'name': 'การลงทุน', 'icon': '📈', 'color': '#20c997'},
            {'name': 'อื่นๆ', 'icon': '💳', 'color': '#6c757d'},
        ]

        # Default expense categories
        expense_categories = [
            {'name': 'อาหาร', 'icon': '🍕', 'color': '#fd7e14'},
            {'name': 'ที่อยู่อาศัย', 'icon': '🏠', 'color': '#e83e8c'},
            {'name': 'การเดินทาง', 'icon': '🚗', 'color': '#20c997'},
            {'name': 'ความบันเทิง', 'icon': '🎬', 'color': '#6f42c1'},
            {'name': 'เสื้อผ้า', 'icon': '👕', 'color': '#dc3545'},
            {'name': 'สุขภาพ', 'icon': '💊', 'color': '#198754'},
            {'name': 'การศึกษา', 'icon': '📚', 'color': '#0dcaf0'},
            {'name': 'ช้อปปิ้ง', 'icon': '🛍️', 'color': '#ffc107'},
            {'name': 'สาธารณูปโภค', 'icon': '⚡', 'color': '#6c757d'},
            {'name': 'อื่นๆ', 'icon': '💳', 'color': '#adb5bd'},
        ]

        created_count = 0
        
        for user in users:
            self.stdout.write(f'Creating categories for user: {user.email}')
            
            # Create income categories
            for cat_data in income_categories:
                category, created = Category.objects.get_or_create(
                    user=user,
                    name=cat_data['name'],
                    category_type='income',
                    defaults={
                        'icon': cat_data['icon'],
                        'color': cat_data['color'],
                        'is_default': True,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created income category: {category.name}')

            # Create expense categories
            for cat_data in expense_categories:
                category, created = Category.objects.get_or_create(
                    user=user,
                    name=cat_data['name'],
                    category_type='expense',
                    defaults={
                        'icon': cat_data['icon'],
                        'color': cat_data['color'],
                        'is_default': True,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created expense category: {category.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} default categories for {users.count()} user(s)'
            )
        )