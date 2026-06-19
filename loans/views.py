from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Loan
from .forms import LoanForm, LoanRepaymentForm
from notifications.models import Notification

class LoanListView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repayment_form'] = LoanRepaymentForm()
        return context

class LoanCreateView(LoginRequiredMixin, CreateView):
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loans:loan_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Loan added successfully.")
        
        # Check if fully paid initially
        if form.instance.status == 'Fully Paid':
            Notification.create_notification(
                user=self.request.user,
                title="Loan Fully Paid!",
                message=f"Congratulations! Your loan '{form.instance.loan_name}' of {form.instance.total_amount} is now fully paid."
            )
        return response

class LoanUpdateView(LoginRequiredMixin, UpdateView):
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loans:loan_list')

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Loan updated successfully.")
        
        if form.instance.status == 'Fully Paid':
            Notification.create_notification(
                user=self.request.user,
                title="Loan Fully Paid!",
                message=f"Congratulations! Your loan '{form.instance.loan_name}' of {form.instance.total_amount} is now fully paid."
            )
        return response

class LoanDeleteView(LoginRequiredMixin, DeleteView):
    model = Loan
    template_name = 'loans/loan_confirm_delete.html'
    success_url = reverse_lazy('loans:loan_list')

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Loan deleted successfully.")
        return super().form_valid(form)

class RepayLoanView(LoginRequiredMixin, View):
    def post(self, request, pk):
        loan = get_object_or_404(Loan, pk=pk, user=request.user)
        form = LoanRepaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            loan.paid_amount += amount
            loan.save()  # Auto updates remaining_amount and status
            
            if loan.status == 'Fully Paid':
                Notification.create_notification(
                    user=request.user,
                    title="Loan Fully Paid!",
                    message=f"Congratulations! Your loan '{loan.loan_name}' of {loan.total_amount} is now fully paid."
                )
                
            messages.success(request, f"Successfully registered repayment of {amount} for loan '{loan.loan_name}'.")
        else:
            messages.error(request, "Failed to register repayment. Invalid amount.")
        return redirect('loans:loan_list')
