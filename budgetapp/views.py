from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from .models import Budget, Expense, SubExpense
from .forms import ExpenseForm, SubExpenseForm
import calendar
from decimal import Decimal

class HomeView(ListView):
    model = Budget
    template_name = 'budgetapp/home.html'
    context_object_name = 'budgets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now().date().replace(day=1)
        
        # Get only manually created budgets
        context['budgets'] = Budget.objects.all().order_by('-month')
        
        # Get next month for the create button
        last_budget = Budget.objects.order_by('-month').first()
        if last_budget:
            next_month = (last_budget.month + relativedelta(months=1)).replace(day=1)
        else:
            next_month = current_date
            
        context['next_month'] = next_month
        return context

def create_next_budget(request):
    if request.method == 'POST':
        last_budget = Budget.objects.order_by('-month').first()
        if last_budget:
            next_month = (last_budget.month + relativedelta(months=1)).replace(day=1)
        else:
            next_month = timezone.now().date().replace(day=1)

        # Create new budget
        budget = Budget.objects.create(month=next_month)

        # Copy recurring expenses from previous month if it exists
        if last_budget:
            recurring_expenses = last_budget.expenses.filter(is_recurring=True)
            for expense in recurring_expenses:
                Expense.objects.create(
                    budget=budget,
                    name=expense.name,
                    amount=expense.amount,
                    is_recurring=True
                )
            
        messages.success(request, f'Budget for {next_month.strftime("%B %Y")} has been created!')
        return redirect('home')
    
    return redirect('home')

def budget_detail(request, year, month):
    budget_date = timezone.datetime(year=year, month=month, day=1).date()
    budget = get_object_or_404(Budget, month=budget_date)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'income':
            income = request.POST.get('income')
            currency = request.POST.get('currency')
            if income:
                budget.income = income
                budget.currency = currency
                budget.save()
        elif form_type == 'expense':
            expense_id = request.POST.get('expense_id')
            if expense_id:  # Edit existing expense
                expense = get_object_or_404(Expense, id=expense_id, budget=budget)
                form = ExpenseForm(request.POST, instance=expense)
            else:  # New expense
                form = ExpenseForm(request.POST)
            
            if form.is_valid():
                expense = form.save(commit=False)
                expense.budget = budget
                expense.save()
        elif form_type == 'delete_expense':
            expense_id = request.POST.get('expense_id')
            if expense_id:
                expense = get_object_or_404(Expense, id=expense_id, budget=budget)
                expense.delete()
        
        return redirect('budget_detail', year=year, month=month)
    else:
        form = ExpenseForm()

    return render(request, 'budgetapp/budget_detail.html', {
        'budget': budget,
        'form': form,
        'expenses': budget.expenses.all(),
        'currency_choices': Budget.get_currency_choices()
    }) 

def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'sub_expense':
            form = SubExpenseForm(request.POST)
            if form.is_valid():
                sub_expense = form.save(commit=False)
                sub_expense.expense = expense
                # Validate that sub_expense amount doesn't exceed remaining amount
                if sub_expense.amount <= expense.get_remaining_amount():
                    sub_expense.save()
        elif form_type == 'edit_sub_expense':
            sub_expense_id = request.POST.get('sub_expense_id')
            if sub_expense_id:
                sub_expense = get_object_or_404(SubExpense, id=sub_expense_id, expense=expense)
                # Calculate the maximum allowed amount for this edit
                max_amount = expense.get_remaining_amount() + sub_expense.amount
                new_amount = Decimal(request.POST.get('amount', 0))
                
                if new_amount <= max_amount:
                    sub_expense.name = request.POST.get('name')
                    sub_expense.amount = new_amount
                    sub_expense.save()
        elif form_type == 'delete_sub_expense':
            sub_expense_id = request.POST.get('sub_expense_id')
            if sub_expense_id:
                sub_expense = get_object_or_404(SubExpense, id=sub_expense_id, expense=expense)
                sub_expense.delete()
        
        return redirect('expense_detail', expense_id=expense_id)
    else:
        form = SubExpenseForm()

    return render(request, 'budgetapp/expense_detail.html', {
        'expense': expense,
        'form': form,
        'sub_expenses': expense.sub_expenses.all(),
    }) 