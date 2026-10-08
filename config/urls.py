from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from analytics import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("api/districts-list/", views.api_districts_list, name="api_districts_list"),
    path("api/summary/", views.api_summary, name="api_summary"),
    path("api/offenses/", views.api_offenses, name="api_offenses"),
    path("api/critical-offenses/", views.api_critical_offenses, name="api_critical_offenses"),
    path("api/categories/", views.api_categories, name="api_categories"),
    path("api/table/", views.api_table_data, name="api_table_data"),
    path("api/export-csv/", views.api_export_csv, name="api_export_csv"),
    path("api/chatbot/", views.api_chatbot, name="api_chatbot"),
    path("api/ask/", views.api_chatbot, name="api_ask"),

    # Backward compatibility aliases
    path("api/states/", views.api_districts_list, name="api_states"),
    path("api/districts/", views.api_offenses, name="api_districts"),
    path("api/trends/", views.api_trends, name="api_trends"),
    path("api/comparison/", views.api_offenses, name="api_comparison"),
    path("api/district-detail/", views.api_district_detail, name="api_district_detail"),
    path("favicon.ico", views.favicon, name="favicon"),

    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.BASE_DIR / "static"}),
]