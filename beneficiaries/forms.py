from django import forms
from .models import FamilyMember

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = [
            'full_name', 'relationship_to_head', 'birthdate', 'age', 
            'gender', 'is_pwd', 'is_senior_citizen', 'is_pregnant', 
            'is_lactating_mother', 'is_solo_parent'
        ]
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }
