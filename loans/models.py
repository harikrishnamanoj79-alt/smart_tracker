from django.db import models
from django.conf import settings
import datetime

class Loan(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Fully Paid', 'Fully Paid'),
        ('Overdue', 'Overdue'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    loan_name = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def save(self, *args, **kwargs):
        self.remaining_amount = self.total_amount - self.paid_amount
        if self.remaining_amount <= 0:
            self.remaining_amount = 0
            self.status = 'Fully Paid'
        elif self.due_date < datetime.date.today():
            self.status = 'Overdue'
        else:
            self.status = 'Active'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_name} (Total: {self.total_amount}, Remaining: {self.remaining_amount})"
