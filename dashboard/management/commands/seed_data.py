import datetime
import random
from django.core.management.base import BaseCommand
from accounts.models import User
from expenses.models import Category, PaymentMethod, Expense
from income.models import Income
from budgets.models import Budget
from savings.models import SavingsGoal
from loans.models import Loan
from dashboard.models import RecurringTransaction

class Command(BaseCommand):
    help = "Seeds database with categories, payment methods, test user and initial transactions."

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # 1. Create Categories
        income_cats = ["Salary", "Freelance", "Investments", "Gifts", "Other Income"]
        expense_cats = ["Food", "Rent & Utilities", "Transportation", "Entertainment", "Shopping", "Medical", "Travel"]

        in_cat_objs = []
        for name in income_cats:
            obj, _ = Category.objects.get_or_create(name=name, type="Income")
            in_cat_objs.append(obj)

        ex_cat_objs = []
        for name in expense_cats:
            obj, _ = Category.objects.get_or_create(name=name, type="Expense")
            ex_cat_objs.append(obj)

        # 2. Create Payment Methods
        pms = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "UPI"]
        pm_objs = []
        for name in pms:
            obj, _ = PaymentMethod.objects.get_or_create(name=name)
            pm_objs.append(obj)

        # 3. Create Test User
        user, created = User.objects.get_or_create(username="testuser", email="testuser@example.com")
        if created:
            user.set_password("Password123")
            user.save()
            self.stdout.write("Created test user: testuser / Password123")
        else:
            self.stdout.write("Test user already exists.")

        # Clear existing data for test user to avoid pollution
        Expense.objects.filter(user=user).delete()
        Income.objects.filter(user=user).delete()
        Budget.objects.filter(user=user).delete()
        SavingsGoal.objects.filter(user=user).delete()
        Loan.objects.filter(user=user).delete()
        RecurringTransaction.objects.filter(user=user).delete()

        # 4. Create Incomes and Expenses spanning last 6 months
        today = datetime.date.today()
        
        # Incomes
        for i in range(6):
            month_date = today - datetime.timedelta(days=i*30)
            # Monthly Salary
            Income.objects.create(
                user=user,
                category=Category.objects.get(name="Salary"),
                amount=50000.00,
                source="Tech Corp Salary",
                date=datetime.date(month_date.year, month_date.month, 1),
                payment_method=PaymentMethod.objects.get(name="Bank Transfer")
            )
            # Side hustle Freelance
            Income.objects.create(
                user=user,
                category=Category.objects.get(name="Freelance"),
                amount=random.choice([8000, 12000, 15000]),
                source="Freelance Client",
                date=datetime.date(month_date.year, month_date.month, random.randint(10, 20)),
                payment_method=PaymentMethod.objects.get(name="UPI")
            )

        # Expenses
        for i in range(120): # ~20 expenses per month
            delta_days = random.randint(0, 180)
            tx_date = today - datetime.timedelta(days=delta_days)
            category = random.choice(ex_cat_objs)
            pm = random.choice(pm_objs)
            
            # Set amount depending on category
            if category.name == "Rent & Utilities":
                amount = random.randint(8000, 12000)
            elif category.name == "Food":
                amount = random.randint(150, 800)
            elif category.name == "Transportation":
                amount = random.randint(50, 500)
            elif category.name == "Entertainment":
                amount = random.randint(500, 2000)
            elif category.name == "Shopping":
                amount = random.randint(1000, 5000)
            else:
                amount = random.randint(300, 1500)

            Expense.objects.create(
                user=user,
                category=category,
                amount=amount,
                description=f"Dummy {category.name} expense",
                date=tx_date,
                payment_method=pm
            )

        # 5. Create Budgets (for current month)
        for cat in ex_cat_objs[:4]:
            Budget.objects.create(
                user=user,
                category=cat,
                monthly_limit=random.choice([2000, 5000, 15000]),
                month=today.month,
                year=today.year
            )

        # 6. Create Savings Goals
        SavingsGoal.objects.create(
            user=user,
            title="Emergency Fund",
            target_amount=100000.00,
            saved_amount=45000.00,
            target_date=today + datetime.timedelta(days=365),
            status="Active"
        )
        SavingsGoal.objects.create(
            user=user,
            title="MacBook Pro",
            target_amount=150000.00,
            saved_amount=150000.00,
            target_date=today - datetime.timedelta(days=10),
            status="Achieved"
        )

        # 7. Create Loans
        Loan.objects.create(
            user=user,
            loan_name="Car Loan",
            total_amount=500000.00,
            paid_amount=150000.00,
            due_date=today + datetime.timedelta(days=730),
            status="Active"
        )

        # 8. Create Recurring Transactions
        RecurringTransaction.objects.create(
            user=user,
            title="Netflix Premium",
            type="Expense",
            amount=649.00,
            frequency="Monthly",
            next_date=today + datetime.timedelta(days=5),
            active=True
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully! Run python manage.py runserver and login as testuser / Password123"))
