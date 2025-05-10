from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=None)
def delete_cache_total_price(*args, **kwargs):
    """
    Сигнал для удаления кеша при удалении подписки.
    """
    from django.core.cache import cache
    from django.conf import settings

    cache.delete(settings.PRICE_CACHE_NAME)