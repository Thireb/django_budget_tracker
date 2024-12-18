from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.cache import cache
from django.utils.text import slugify
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce

class Budget(models.Model):
    """
    Represents a monthly budget with income and expenses.
    """
    month: models.DateField = models.DateField()
    income: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency: models.CharField = models.CharField(max_length=3, default='PKR')
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    is_archived: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        ordering = ['-month']
        verbose_name_plural = 'Budgets'
        indexes = [
            models.Index(fields=['-month']),
        ]

    def __str__(self):
        return self.month.strftime("%B %Y")

    def was_edited(self):
        """Return True if the budget was edited after creation"""
        return self.updated_at > self.created_at

    def get_remaining_budget(self):
        """Calculate remaining budget after all expenses"""
        total_expenses = self.expenses.aggregate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['total']
        
        return self.income - total_expenses if self.income else Decimal('0.00')

    @staticmethod
    def get_currency_choices():
        # Common currencies with their names
        currencies = [
            ('PKR', 'PKR - Pakistani Rupee'),
            ('USD', 'USD - US Dollar'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
            ('AUD', 'AUD - Australian Dollar'),
            ('CAD', 'CAD - Canadian Dollar'),
            ('JPY', 'JPY - Japanese Yen'),
            ('CNY', 'CNY - Chinese Yuan'),
            ('INR', 'INR - Indian Rupee'),
            ('AED', 'AED - UAE Dirham'),
            ('SAR', 'SAR - Saudi Riyal'),
        ]
        return currencies

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default="#000000", help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='expenses')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='expenses'
    )

    def __str__(self):
        return f"{self.name} - {self.amount}"

    def get_remaining_amount(self):
        total_sub_expenses = self.sub_expenses.aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        return self.amount - total_sub_expenses

class SubExpense(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='sub_expenses')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"

class BudgetLog(models.Model):
    ACTIONS = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    )
    
    month = models.DateField()
    action = models.CharField(max_length=10, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} - {self.month.strftime('%B %Y')}" 

class ArchivedBudget(models.Model):
    budget = models.OneToOneField('Budget', on_delete=models.CASCADE)
    archived_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-budget__month']

    def __str__(self):
        return f"Archive: {self.budget.month.strftime('%Y-%m')}" 

class BudgetDeletionLog(models.Model):
    month = models.DateField()
    deleted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-deleted_at']
    
    def __str__(self):
        return f"Budget for {self.month.strftime('%B %Y')} deleted on {self.deleted_at.strftime('%Y-%m-%d %H:%M')}"

class IncomeHistory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='income_history')
    old_amount = models.DecimalField(max_digits=10, decimal_places=2)
    new_amount = models.DecimalField(max_digits=10, decimal_places=2)
    old_currency = models.CharField(max_length=3)
    new_currency = models.CharField(max_length=3)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Income histories'

    def __str__(self):
        return f"Income change for {self.budget.month.strftime('%B %Y')}"

class RecentUpdate(models.Model):
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='recent_updates')
    action_type = models.CharField(max_length=50)  # e.g., 'expense_added', 'income_updated'
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.description}"