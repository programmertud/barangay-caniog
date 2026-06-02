from django.db import models

class Item(models.Model):
    UNIT_CHOICES = (
        ('PCS', 'Pieces'),
        ('KG', 'Kilograms'),
        ('L', 'Liters'),
        ('BOX', 'Boxes'),
        ('KIT', 'Kits'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100) # e.g., Food, Medicine, Hygiene
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='PCS')
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('ADD', 'Stock Addition'),
        ('DEDUCT', 'Stock Deduction'),
        ('ADJUST', 'Manual Adjustment'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.item.name} ({self.quantity})"

class Kit(models.Model):
    name = models.CharField(max_length=200) # e.g., Family Food Pack (FFP)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class KitItem(models.Model):
    kit = models.ForeignKey(Kit, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1) # How many of this item go in one kit

    def __str__(self):
        return f"{self.quantity}x {self.item.name} in {self.kit.name}"
