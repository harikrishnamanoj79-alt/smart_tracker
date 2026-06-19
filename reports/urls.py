from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportDashboardView.as_view(), name='report_dashboard'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
    path('export/excel/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/csv/', views.ExportCSVView.as_view(), name='export_csv'),
]
