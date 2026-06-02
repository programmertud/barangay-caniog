from django.db import models
from django.utils.crypto import get_random_string
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priority_score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Beneficiary(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )
    PRIORITY_LEVELS = (
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
    )
    CLAIM_STATUS = (
        ('PENDING', 'Pending'),
        ('CLAIMED', 'Claimed'),
        ('PARTIAL', 'Partially Claimed'),
    )

    # Basic Info
    full_name = models.CharField(max_length=255)
    dafac_number = models.CharField(max_length=100, null=True, blank=True, unique=True, verbose_name="DAFAC Card #")
    address = models.TextField()
    barangay = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    birthdate = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Household Info
    household_number = models.CharField(max_length=50)
    family_member_count = models.IntegerField(default=1)
    children_count = models.IntegerField(default=0)
    elderly_count = models.IntegerField(default=0)
    pwd_count = models.IntegerField(default=0)
    
    # Socio-economic Info
    employment_status = models.CharField(max_length=100)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    house_condition = models.CharField(max_length=100) # e.g., Concrete, Wooden, Shanty
    
    # System Info
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
    priority_score = models.IntegerField(default=0)
    priority_level = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='LOW')
    claim_status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='PENDING')
    
    # Files
    valid_id_photo = models.ImageField(upload_to='beneficiaries/ids/', blank=True, null=True)
    beneficiary_photo = models.ImageField(upload_to='beneficiaries/photos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='beneficiaries/qr/', blank=True, null=True)
    claim_reference_number = models.CharField(max_length=12, unique=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.claim_reference_number:
            self.claim_reference_number = get_random_string(12).upper()
        
        # Calculate priority
        self.calculate_priority()
        
        # Generate QR Code
        if not self.qr_code:
            self.generate_qr()
            
        super().save(*args, **kwargs)

    def update_counts(self):
        """Automatically update household counts based on family members."""
        members = self.family_members.all()
        self.family_member_count = members.count() + 1 # +1 for the head
        self.children_count = members.filter(age__lt=18).count()
        self.elderly_count = members.filter(is_senior_citizen=True).count()
        if self.age >= 60: self.elderly_count += 1
        self.pwd_count = members.filter(is_pwd=True).count()
        self.save()

    def calculate_priority(self):
        score = 0
        if self.category:
            score += self.category.priority_score
        
        # Additional scoring logic
        if self.monthly_income < 5000: score += 5
        elif self.monthly_income < 10000: score += 3
        
        if self.pwd_count > 0: score += 4
        if self.elderly_count > 0: score += 3
        if self.children_count > 3: score += 2
        
        self.priority_score = score
        
        if score >= 10: self.priority_level = 'HIGH'
        elif score >= 5: self.priority_level = 'MEDIUM'
        else: self.priority_level = 'LOW'

    def generate_qr(self):
        qr_data = f"REF:{self.claim_reference_number}|NAME:{self.full_name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.claim_reference_number}.png'
        self.qr_code.save(filename, File(buffer), save=False)

    def __str__(self):
        return self.full_name

class FamilyMember(models.Model):
    RELATIONSHIP_CHOICES = (
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('OTHER', 'Other Relative'),
    )
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='family_members')
    full_name = models.CharField(max_length=255)
    relationship_to_head = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    birthdate = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=Beneficiary.GENDER_CHOICES)
    
    # Vulnerability Status (DSWD standard)
    is_pwd = models.BooleanField(default=False, verbose_name="PWD")
    is_senior_citizen = models.BooleanField(default=False)
    is_pregnant = models.BooleanField(default=False)
    is_lactating_mother = models.BooleanField(default=False)
    is_solo_parent = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Trigger update on the head beneficiary
        self.beneficiary.update_counts()

    def delete(self, *args, **kwargs):
        beneficiary = self.beneficiary
        super().delete(*args, **kwargs)
        beneficiary.update_counts()

    def __str__(self):
        return f"{self.full_name} ({self.relationship_to_head})"
