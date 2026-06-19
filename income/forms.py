from django import forms
from .models import Income
from expenses.models import Category

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ('category', 'amount', 'source', 'description', 'date', 'payment_method')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Source of income (e.g. Salary, Client)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional details'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='Income')
