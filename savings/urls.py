from django.urls import path
from . import views

app_name = 'savings'

urlpatterns = [
    path('', views.SavingsGoalListView.as_view(), name='savings_list'),
    path('add/', views.SavingsGoalCreateView.as_view(), name='savings_add'),
    path('<int:pk>/edit/', views.SavingsGoalUpdateView.as_view(), name='savings_edit'),
    path('<int:pk>/delete/', views.SavingsGoalDeleteView.as_view(), name='savings_delete'),
    path('<int:pk>/deposit/', views.AddSavingsView.as_view(), name='savings_deposit'),
]
