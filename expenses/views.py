from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from .models import Category, PaymentMethod, Expense
from .forms import CategoryForm, PaymentMethodForm, ExpenseForm
from budgets.models import Budget
from notifications.models import Notification
import datetime

# Helper to check budget status
def check_budget_status(user, category, date):
    budget = Budget.objects.filter(user=user, category=category, month=date.month, year=date.year).first()
    if budget:
        total_spent = Expense.objects.filter(
            user=user,
            category=category,
            date__month=date.month,
            date__year=date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        if total_spent > budget.monthly_limit:
            msg = f"You have exceeded your monthly budget of {budget.monthly_limit} for category '{category.name}'. Current spending: {total_spent}."
            # Check if notification already exists to prevent duplicate spam
            existing_notif = Notification.objects.filter(
                user=user,
                title="Budget Exceeded Alert",
                message=msg
            ).exists()
            if not existing_notif:
                Notification.create_notification(user=user, title="Budget Exceeded Alert", message=msg)
            return True, msg
    return False, ""

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully.")
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'expenses/category_confirm_delete.html'
    success_url = reverse_lazy('expenses:category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category deleted successfully.")
        return super().form_valid(form)


# Payment Method Views
class PaymentMethodListView(LoginRequiredMixin, ListView):
    model = PaymentMethod
    template_name = 'expenses/payment_method_list.html'
    context_object_name = 'payment_methods'

class PaymentMethodCreateView(LoginRequiredMixin, CreateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'expenses/payment_method_form.html'
    success_url = reverse_lazy('expenses:payment_method_list')

    def form_valid(self, form):
        messages.success(self.request, "Payment method created successfully.")
        return super().form_valid(form)

class PaymentMethodUpdateView(LoginRequiredMixin, UpdateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'expenses/payment_method_form.html'
    success_url = reverse_lazy('expenses:payment_method_list')

    def form_valid(self, form):
        messages.success(self.request, "Payment method updated successfully.")
        return super().form_valid(form)

class PaymentMethodDeleteView(LoginRequiredMixin, DeleteView):
    model = PaymentMethod
    template_name = 'expenses/payment_method_confirm_delete.html'
    success_url = reverse_lazy('expenses:payment_method_list')

    def form_valid(self, form):
        messages.success(self.request, "Payment method deleted successfully.")
        return super().form_valid(form)


# Expense Views
class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user).select_related('category', 'payment_method')
        
        # Filters
        category_id = self.request.GET.get('category')
        payment_method_id = self.request.GET.get('payment_method')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        search_query = self.request.GET.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if payment_method_id:
            queryset = queryset.filter(payment_method_id=payment_method_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if search_query:
            queryset = queryset.filter(description__icontains=search_query)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(type='Expense')
        context['payment_methods'] = PaymentMethod.objects.all()
        # Add filter values back to context
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_payment_method'] = self.request.GET.get('payment_method', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:expense_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Expense added successfully.")
        
        # Check budget
        exceeded, msg = check_budget_status(self.request.user, form.instance.category, form.instance.date)
        if exceeded:
            messages.warning(self.request, msg)
            
        return response

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:expense_list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Expense updated successfully.")
        
        # Check budget
        exceeded, msg = check_budget_status(self.request.user, form.instance.category, form.instance.date)
        if exceeded:
            messages.warning(self.request, msg)
            
        return response

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expenses:expense_list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Expense deleted successfully.")
        return super().form_valid(form)
