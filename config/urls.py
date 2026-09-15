from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from analytics import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("api/states/", views.api_states, name="api_states"),
    path("api/summary/", views.api_summary, name="api_summary"),
    path("api/trends/", views.api_trends, name="api_trends"),
    path("api/districts/", views.api_districts, name="api_districts"),
    path("api/categories/", views.api_categories, name="api_categories"),
    path("api/district-detail/", views.api_district_detail, name="api_district_detail"),
    path("api/table/", views.api_table_data, name="api_table_data"),
    path("api/export-csv/", views.api_export_csv, name="api_export_csv"),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.BASE_DIR / "static"}),
]