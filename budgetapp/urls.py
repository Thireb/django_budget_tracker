from django.urls import path
from .views import HomeView, budget_detail, expense_detail, create_next_budget, delete_budget, get_next_month, archive_budget, view_archives, delete_archived_budget, category_list, category_edit, category_delete

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('budget/<int:year>/<int:month>/', budget_detail, name='budget_detail'),
    path('expense/<int:expense_id>/', expense_detail, name='expense_detail'),
    path('create-next-budget/', create_next_budget, name='create_next_budget'),
    path('budget/delete/<str:year_month>/', delete_budget, name='delete_budget'),
    path('get-next-month/', get_next_month, name='get_next_month'),
    path('budget/archive/<str:year_month>/', archive_budget, name='archive_budget'),
    path('archives/', view_archives, name='view_archives'),
    path('archives/delete/<str:year_month>/', delete_archived_budget, name='delete_archived_budget'),
    path('categories/', category_list, name='category_list'),
    path('categories/<slug:slug>/edit/', category_edit, name='category_edit'),
    path('categories/<slug:slug>/delete/', category_delete, name='category_delete'),
] 