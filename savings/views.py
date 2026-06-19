from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import SavingsGoal
from .forms import SavingsGoalForm, SavingsAddForm
from notifications.models import Notification

class SavingsGoalListView(LoginRequiredMixin, ListView):
    model = SavingsGoal
    template_name = 'savings/savings_list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deposit_form'] = SavingsAddForm()
        return context

class SavingsGoalCreateView(LoginRequiredMixin, CreateView):
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'savings/savings_form.html'
    success_url = reverse_lazy('savings:savings_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Check if saved_amount >= target_amount
        if form.instance.saved_amount >= form.instance.target_amount:
            form.instance.status = 'Achieved'
            Notification.create_notification(
                user=self.request.user,
                title="Savings Goal Achieved!",
                message=f"Congratulations! You have reached your savings goal '{form.instance.title}' of {form.instance.target_amount}!"
            )
            
        messages.success(self.request, "Savings Goal created successfully.")
        return super().form_valid(form)

class SavingsGoalUpdateView(LoginRequiredMixin, UpdateView):
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'savings/savings_form.html'
    success_url = reverse_lazy('savings:savings_list')

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def form_valid(self, form):
        if form.instance.saved_amount >= form.instance.target_amount:
            if form.instance.status != 'Achieved':
                form.instance.status = 'Achieved'
                Notification.create_notification(
                    user=self.request.user,
                    title="Savings Goal Achieved!",
                    message=f"Congratulations! You have reached your savings goal '{form.instance.title}' of {form.instance.target_amount}!"
                )
        else:
            if form.instance.status == 'Achieved':
                form.instance.status = 'Active'
                
        messages.success(self.request, "Savings Goal updated successfully.")
        return super().form_valid(form)

class SavingsGoalDeleteView(LoginRequiredMixin, DeleteView):
    model = SavingsGoal
    template_name = 'savings/savings_confirm_delete.html'
    success_url = reverse_lazy('savings:savings_list')

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Savings Goal deleted successfully.")
        return super().form_valid(form)

class AddSavingsView(LoginRequiredMixin, View):
    def post(self, request, pk):
        goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
        form = SavingsAddForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            goal.saved_amount += amount
            
            # Check achievement status
            if goal.saved_amount >= goal.target_amount:
                goal.saved_amount = goal.target_amount
                if goal.status != 'Achieved':
                    goal.status = 'Achieved'
                    Notification.create_notification(
                        user=request.user,
                        title="Savings Goal Achieved!",
                        message=f"Congratulations! You have reached your savings goal '{goal.title}' of {goal.target_amount}!"
                    )
            else:
                if goal.status == 'Achieved':
                    goal.status = 'Active'
                    
            goal.save()
            messages.success(request, f"Successfully deposited {amount} to '{goal.title}'.")
        else:
            messages.error(request, "Failed to deposit savings. Invalid amount.")
        return redirect('savings:savings_list')
