from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Payment Methods
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment_method_list'),
    path('payment-methods/add/', views.PaymentMethodCreateView.as_view(), name='payment_method_add'),
    path('payment-methods/<int:pk>/edit/', views.PaymentMethodUpdateView.as_view(), name='payment_method_edit'),
    path('payment-methods/<int:pk>/delete/', views.PaymentMethodDeleteView.as_view(), name='payment_method_delete'),

    # Expenses
    path('', views.ExpenseListView.as_view(), name='expense_list'),
    path('add/', views.ExpenseCreateView.as_view(), name='expense_add'),
    path('<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_edit'),
    path('<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
]
