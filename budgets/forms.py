from django import forms
from .models import Budget
from expenses.models import Category
import datetime

class BudgetForm(forms.ModelForm):
    MONTH_CHOICES = [(i, datetime.date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    YEAR_CHOICES = [(y, y) for y in range(datetime.date.today().year - 2, datetime.date.today().year + 5)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Budget
        fields = ('category', 'monthly_limit', 'month', 'year')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(type='Expense')
        
        if not self.instance.pk:
            self.fields['month'].initial = datetime.date.today().month
            self.fields['year'].initial = datetime.date.today().year
