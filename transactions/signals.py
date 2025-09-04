from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Transaction

@receiver(post_save, sender=Transaction)
def invalidate_dashboard_cache_on_save(sender, instance, **kwargs):
    """Invalidate dashboard cache when a transaction is saved"""
    cache_pattern = f"dashboard_stats_{instance.user.id}_*"
    # Delete all cache keys for this user's dashboard
    cache.delete_many([
        f"dashboard_stats_{instance.user.id}_dashboard_{instance.date.strftime('%Y%m%d')}",
        f"dashboard_stats_{instance.user.id}_",
    ])

@receiver(post_delete, sender=Transaction)
def invalidate_dashboard_cache_on_delete(sender, instance, **kwargs):
    """Invalidate dashboard cache when a transaction is deleted"""
    cache_pattern = f"dashboard_stats_{instance.user.id}_*"
    # Delete all cache keys for this user's dashboard
    cache.delete_many([
        f"dashboard_stats_{instance.user.id}_dashboard_{instance.date.strftime('%Y%m%d')}",
        f"dashboard_stats_{instance.user.id}_",
    ])