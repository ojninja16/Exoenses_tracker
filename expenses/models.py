from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User

class Expense(models.Model):
    SPLIT_CHOICES = [
        ('EQUAL', 'Equal Split'),
        ('EXACT', 'Exact Amount'),
        ('PERCENTAGE', 'Percentage Split'),
    ]

    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_type = models.CharField(max_length=10, choices=SPLIT_CHOICES)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_splits')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ('expense', 'user')

    def __str__(self):
        return f"{self.expense.title} - {self.user.email}"

# Create your models here.
