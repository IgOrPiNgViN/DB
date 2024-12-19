from django.urls import path
from db_app import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'db_app'

urlpatterns = [
    # Для входа:
    path('login/', auth_views.LoginView.as_view(), name='login'),
    # Для выхода:
    path('logout/', auth_views.LogoutView.as_view(next_page='db_app:list_tables'), name='logout'),
    path('', views.list_tables, name='list_tables'),
    path('count_bookings/', views.count_bookings, name='count_bookings'),
    path('bookings/', views.view_bookings, name='view_bookings'),
    path('<str:table_name>/', views.view_table, name='view_table'),
    path('<str:table_name>/edit/<int:key>/', views.edit_record, name='edit_record'),
    path('<str:table_name>/delete/<int:key>/', views.delete_record, name='delete_record'),
    path('add/<str:table_name>', views.add_record, name='add_record')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)