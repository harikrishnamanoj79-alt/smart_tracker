from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.LoanListView.as_view(), name='loan_list'),
    path('add/', views.LoanCreateView.as_view(), name='loan_add'),
    path('<int:pk>/edit/', views.LoanUpdateView.as_view(), name='loan_edit'),
    path('<int:pk>/delete/', views.LoanDeleteView.as_view(), name='loan_delete'),
    path('<int:pk>/repay/', views.RepayLoanView.as_view(), name='loan_repay'),
]
