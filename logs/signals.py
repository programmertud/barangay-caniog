from django.db.models.signals import post_save
from django.dispatch import receiver
from beneficiaries.models import Beneficiary
from inventory.models import Item, Kit
from events.models import ReliefEvent
from distribution.models import Distribution
from logs.models import ActivityLog
from logs.middleware import get_current_user, get_current_ip

@receiver(post_save, sender=Beneficiary)
def log_beneficiary_activity(sender, instance, created, **kwargs):
    action = "Registration" if created else "Update"
    ActivityLog.objects.create(
        user=get_current_user(),
        action=f"Beneficiary {action}",
        module="beneficiaries",
        description=f"{action} of beneficiary: {instance.full_name}",
        ip_address=get_current_ip()
    )

@receiver(post_save, sender=Item)
def log_inventory_activity(sender, instance, created, **kwargs):
    action = "Addition" if created else "Update"
    ActivityLog.objects.create(
        user=get_current_user(),
        action=f"Item {action}",
        module="inventory",
        description=f"{action} of item: {instance.name} (Qty: {instance.stock_quantity})",
        ip_address=get_current_ip()
    )

@receiver(post_save, sender=ReliefEvent)
def log_event_activity(sender, instance, created, **kwargs):
    action = "Creation" if created else "Update"
    ActivityLog.objects.create(
        user=get_current_user(),
        action=f"Event {action}",
        module="events",
        description=f"{action} of relief event: {instance.title}",
        ip_address=get_current_ip()
    )

@receiver(post_save, sender=Distribution)
def log_distribution_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=get_current_user(),
            action="Relief Distribution",
            module="distribution",
            description=f"Distribution recorded for: {instance.beneficiary.full_name} in event {instance.event.title}",
            ip_address=get_current_ip()
        )
