from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from .models import Budget
from .forms import BudgetForm
from expenses.models import Expense
import datetime

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budget_data = []
        for budget in self.get_queryset():
            total_spent = Expense.objects.filter(
                user=self.request.user,
                category=budget.category,
                date__month=budget.month,
                date__year=budget.year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            percentage = 0
            if budget.monthly_limit > 0:
                percentage = (total_spent / budget.monthly_limit) * 100
                percentage = round(min(percentage, 100), 2)
            
            remaining = budget.monthly_limit - total_spent
            
            budget_data.append({
                'budget': budget,
                'total_spent': total_spent,
                'remaining': remaining,
                'percentage': percentage,
                'status_class': 'danger' if total_spent > budget.monthly_limit else ('warning' if percentage >= 85 else 'success'),
                'month_name': datetime.date(2000, budget.month, 1).strftime('%B')
            })
        context['budget_data'] = budget_data
        return context

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:budget_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Check if budget already exists for this category/month/year combination
        existing = Budget.objects.filter(
            user=self.request.user,
            category=form.cleaned_data['category'],
            month=form.cleaned_data['month'],
            year=form.cleaned_data['year']
        ).exists()
        
        if existing:
            form.add_error(None, "A budget for this category, month, and year already exists.")
            return self.form_invalid(form)
            
        messages.success(self.request, "Budget limit set successfully.")
        return super().form_valid(form)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:budget_list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Budget updated successfully.")
        return super().form_valid(form)

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = 'budgets/budget_confirm_delete.html'
    success_url = reverse_lazy('budgets:budget_list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Budget deleted successfully.")
        return super().form_valid(form)
