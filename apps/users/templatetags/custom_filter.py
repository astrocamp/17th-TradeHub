from django import template
from apps.users.models import Notification

register = template.Library()

@register.filter
def is_distinct(notification):
    notifications = Notification.objects.filter(sender_state=notification.sender_state, message=notification.message)
    return notifications.count() == 1
        
    