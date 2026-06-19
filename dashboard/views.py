from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum
from django.http import JsonResponse
from .models import RecurringTransaction
from .forms import RecurringTransactionForm
from income.models import Income
from expenses.models import Expense, Category
from savings.models import SavingsGoal
from loans.models import Loan
from budgets.models import Budget
from notifications.models import Notification
import datetime

# Helper to process pending recurring transactions
def process_recurring_transactions(user):
    today = datetime.date.today()
    pending = RecurringTransaction.objects.filter(user=user, active=True, next_date__lte=today)
    
    # Pre-fetch default categories and payment methods (or default dummy)
    from expenses.models import Category, PaymentMethod
    default_pm = PaymentMethod.objects.first()
    
    for tx in pending:
        # Create corresponding Income or Expense
        if tx.type == 'Income':
            cat = Category.objects.filter(type='Income').first()
            if not cat:
                cat = Category.objects.create(name="Miscellaneous", type="Income")
            Income.objects.create(
                user=user,
                category=cat,
                amount=tx.amount,
                source=tx.title,
                description=f"Auto-generated recurring income: {tx.title}",
                date=tx.next_date,
                payment_method=default_pm
            )
            Notification.create_notification(
                user=user,
                title="Recurring Income Processed",
                message=f"Your recurring income '{tx.title}' of {tx.amount} has been added automatically."
            )
        else:
            cat = Category.objects.filter(type='Expense').first()
            if not cat:
                cat = Category.objects.create(name="Miscellaneous", type="Expense")
            Expense.objects.create(
                user=user,
                category=cat,
                amount=tx.amount,
                description=f"Auto-generated recurring expense: {tx.title}",
                date=tx.next_date,
                payment_method=default_pm
            )
            Notification.create_notification(
                user=user,
                title="Recurring Expense Processed",
                message=f"Your recurring expense '{tx.title}' of {tx.amount} has been added automatically."
            )
        
        # Calculate next date
        if tx.frequency == 'Daily':
            tx.next_date = tx.next_date + datetime.timedelta(days=1)
        elif tx.frequency == 'Weekly':
            tx.next_date = tx.next_date + datetime.timedelta(weeks=1)
        elif tx.frequency == 'Monthly':
            # Approximate a month
            tx.next_date = tx.next_date + datetime.timedelta(days=30)
        elif tx.frequency == 'Yearly':
            # Approximate a year
            tx.next_date = tx.next_date + datetime.timedelta(days=365)
            
        tx.save()

class DashboardHomeView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        
        # Process recurring transactions on load
        process_recurring_transactions(user)
        
        # Widgets calculations
        total_income = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
        current_balance = total_income - total_expense
        
        savings_amount = SavingsGoal.objects.filter(user=user).aggregate(total=Sum('saved_amount'))['total'] or 0
        active_loans = Loan.objects.filter(user=user, status__in=['Active', 'Overdue']).count()
        
        # Monthly budget usage
        today = datetime.date.today()
        monthly_budgets = Budget.objects.filter(user=user, month=today.month, year=today.year)
        total_budget_limit = monthly_budgets.aggregate(total=Sum('monthly_limit'))['total'] or 0
        
        total_budget_spent = 0
        for b in monthly_budgets:
            spent = Expense.objects.filter(
                user=user,
                category=b.category,
                date__month=today.month,
                date__year=today.year
            ).aggregate(total=Sum('amount'))['total'] or 0
            total_budget_spent += spent
            
        budget_usage_percentage = 0
        if total_budget_limit > 0:
            budget_usage_percentage = (total_budget_spent / total_budget_limit) * 100
            budget_usage_percentage = min(round(budget_usage_percentage, 2), 100)
            
        # Recent Transactions (Combine Income and Expense)
        incomes = Income.objects.filter(user=user).order_by('-date')[:5]
        expenses = Expense.objects.filter(user=user).order_by('-date')[:5]
        
        transactions = []
        for inc in incomes:
            transactions.append({
                'type': 'Income',
                'title': inc.source,
                'category': inc.category.name,
                'amount': inc.amount,
                'date': inc.date,
                'class': 'success'
            })
        for exp in expenses:
            transactions.append({
                'type': 'Expense',
                'title': exp.description or exp.category.name,
                'category': exp.category.name,
                'amount': exp.amount,
                'date': exp.date,
                'class': 'danger'
            })
            
        # Sort combined list by date desc
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)[:5]
        
        # Recurring transactions list
        recurring_txs = RecurringTransaction.objects.filter(user=user)

        context = {
            'total_income': total_income,
            'total_expense': total_expense,
            'current_balance': current_balance,
            'savings_amount': savings_amount,
            'active_loans': active_loans,
            'total_budget_limit': total_budget_limit,
            'total_budget_spent': total_budget_spent,
            'budget_usage_percentage': budget_usage_percentage,
            'transactions': transactions,
            'recurring_txs': recurring_txs
        }
        return render(request, 'dashboard/home.html', context)

# JSON Endpoint for charts data
class ChartDataView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        today = datetime.date.today()
        
        # 1. Income vs Expense last 6 months
        months_labels = []
        income_data = []
        expense_data = []
        
        for i in range(5, -1, -1):
            date = today - datetime.timedelta(days=i*30)
            month_num = date.month
            year_num = date.year
            months_labels.append(date.strftime('%B %Y'))
            
            inc_sum = Income.objects.filter(user=user, date__month=month_num, date__year=year_num).aggregate(total=Sum('amount'))['total'] or 0
            exp_sum = Expense.objects.filter(user=user, date__month=month_num, date__year=year_num).aggregate(total=Sum('amount'))['total'] or 0
            
            income_data.append(float(inc_sum))
            expense_data.append(float(exp_sum))
            
        # 2. Expense Category Pie Chart (Current month)
        categories = Category.objects.filter(type='Expense')
        cat_labels = []
        cat_data = []
        
        for cat in categories:
            sum_val = Expense.objects.filter(
                user=user,
                category=cat,
                date__month=today.month,
                date__year=today.year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if sum_val > 0:
                cat_labels.append(cat.name)
                cat_data.append(float(sum_val))
                
        # 3. Monthly Spending Trend last 30 days (Bar Chart)
        days_labels = []
        days_spending = []
        for d in range(29, -1, -1):
            target_date = today - datetime.timedelta(days=d)
            days_labels.append(target_date.strftime('%b %d'))
            spent = Expense.objects.filter(user=user, date=target_date).aggregate(total=Sum('amount'))['total'] or 0
            days_spending.append(float(spent))
            
        # 4. Savings Progress Goals Chart
        goals = SavingsGoal.objects.filter(user=user)
        savings_labels = [g.title for g in goals]
        savings_targets = [float(g.target_amount) for g in goals]
        savings_saved = [float(g.saved_amount) for g in goals]
        
        data = {
            'months_labels': months_labels,
            'income_data': income_data,
            'expense_data': expense_data,
            'cat_labels': cat_labels,
            'cat_data': cat_data,
            'days_labels': days_labels,
            'days_spending': days_spending,
            'savings_labels': savings_labels,
            'savings_targets': savings_targets,
            'savings_saved': savings_saved,
        }
        return JsonResponse(data)


# Recurring Transactions CRUD
class RecurringCreateView(LoginRequiredMixin, CreateView):
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'dashboard/recurring_form.html'
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Recurring transaction created.")
        return super().form_valid(form)

class RecurringUpdateView(LoginRequiredMixin, UpdateView):
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'dashboard/recurring_form.html'
    success_url = reverse_lazy('dashboard:home')

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Recurring transaction updated.")
        return super().form_valid(form)

class RecurringDeleteView(LoginRequiredMixin, DeleteView):
    model = RecurringTransaction
    template_name = 'dashboard/recurring_confirm_delete.html'
    success_url = reverse_lazy('dashboard:home')

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Recurring transaction deleted.")
        return super().form_valid(form)
