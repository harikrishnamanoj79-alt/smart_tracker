from django.db import models
from django.conf import settings
from expenses.models import Category

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()  # 1 to 12
    year = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'category', 'month', 'year'], name='unique_user_category_budget_per_month')
        ]

    def __str__(self):
        return f"{self.user.username} Budget: {self.category.name} - {self.monthly_limit} for {self.month}/{self.year}"
