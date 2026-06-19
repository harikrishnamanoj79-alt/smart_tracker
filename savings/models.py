from django.db import models
from django.conf import settings

class SavingsGoal(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Achieved', 'Achieved'),
        ('Failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='savings_goals')
    title = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def progress_percentage(self):
        if self.target_amount <= 0:
            return 0
        percentage = (self.saved_amount / self.target_amount) * 100
        return min(round(percentage, 2), 100)

    def is_completed(self):
        return self.saved_amount >= self.target_amount

    def __str__(self):
        return f"{self.title} - Goal: {self.target_amount} (Saved: {self.saved_amount})"
