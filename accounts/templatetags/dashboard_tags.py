from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def currency_format(value):
    """Format a number as currency"""
    if value is None:
        return "฿0.00"
    try:
        return f"฿{float(value):,.2f}"
    except (ValueError, TypeError):
        return "฿0.00"

@register.filter
def percentage_change(current, previous):
    """Calculate percentage change between two values"""
    if not previous or previous == 0:
        return 0
    try:
        change = ((float(current) - float(previous)) / float(previous)) * 100
        return round(change, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def trend_class(value):
    """Return CSS class based on positive/negative value"""
    try:
        val = float(value)
        if val > 0:
            return "text-success"
        elif val < 0:
            return "text-danger"
        else:
            return "text-muted"
    except (ValueError, TypeError):
        return "text-muted"

@register.filter
def trend_icon(value):
    """Return trend icon based on positive/negative value"""
    try:
        val = float(value)
        if val > 0:
            return mark_safe('<i class="fas fa-arrow-up text-success"></i>')
        elif val < 0:
            return mark_safe('<i class="fas fa-arrow-down text-danger"></i>')
        else:
            return mark_safe('<i class="fas fa-minus text-muted"></i>')
    except (ValueError, TypeError):
        return mark_safe('<i class="fas fa-minus text-muted"></i>')

@register.inclusion_tag('includes/stat_card.html')
def stat_card(title, value, icon, color="primary", subtitle="", trend=None):
    """Render a statistics card"""
    return {
        'title': title,
        'value': value,
        'icon': icon,
        'color': color,
        'subtitle': subtitle,
        'trend': trend,
    }

@register.filter
def json_script_safe(value):
    """Convert Python data to JSON for use in templates safely"""
    return mark_safe(json.dumps(value))

@register.simple_tag
def transaction_type_badge(transaction_type):
    """Return a colored badge for transaction type"""
    if transaction_type == 'income':
        return format_html(
            '<span class="badge bg-success"><i class="fas fa-plus me-1"></i>รายรับ</span>'
        )
    elif transaction_type == 'expense':
        return format_html(
            '<span class="badge bg-danger"><i class="fas fa-minus me-1"></i>รายจ่าย</span>'
        )
    return format_html('<span class="badge bg-secondary">ไม่ระบุ</span>')

@register.filter
def multiply(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)