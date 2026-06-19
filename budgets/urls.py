from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.BudgetListView.as_view(), name='budget_list'),
    path('add/', views.BudgetCreateView.as_view(), name='budget_add'),
    path('<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit'),
    path('<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
]
