from django.db import models

class Distribution(models.Model):
    event = models.ForeignKey('events.ReliefEvent', on_delete=models.CASCADE, related_name='distributions')
    beneficiary = models.ForeignKey('beneficiaries.Beneficiary', on_delete=models.CASCADE, related_name='distributions')
    distributed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='processed_distributions')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Proof of distribution
    proof_photo = models.ImageField(upload_to='distributions/proofs/', blank=True, null=True)
    signature = models.ImageField(upload_to='distributions/signatures/', blank=True, null=True)
    notes = models.TextField(blank=True)
    
    verification_status = models.BooleanField(default=False) # Verified via QR or Manual
    
    def __str__(self):
        return f"Dist: {self.beneficiary.full_name} - {self.event.title}"

class DistributionItem(models.Model):
    distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey('inventory.Item', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.inventory_item.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Automatically deduct inventory when a distribution item is saved
        if not self.pk: # Only on creation
            self.inventory_item.stock_quantity -= self.quantity
            self.inventory_item.save()
            
            # Log transaction
            from inventory.models import InventoryTransaction
            InventoryTransaction.objects.create(
                item=self.inventory_item,
                transaction_type='DEDUCT',
                quantity=self.quantity,
                reason=f"Distribution for {self.distribution.beneficiary.full_name}",
                performed_by=self.distribution.distributed_by
            )
        super().save(*args, **kwargs)
