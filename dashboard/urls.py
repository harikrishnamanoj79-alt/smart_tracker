from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('chart-data/', views.ChartDataView.as_view(), name='chart_data'),
    path('recurring/add/', views.RecurringCreateView.as_view(), name='recurring_add'),
    path('recurring/<int:pk>/edit/', views.RecurringUpdateView.as_view(), name='recurring_edit'),
    path('recurring/<int:pk>/delete/', views.RecurringDeleteView.as_view(), name='recurring_delete'),
]
