from django.shortcuts import render, redirect
from django.db import connection
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.forms import modelform_factory
from .models import *  # Импортируем все модели
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict


EXCLUDED_TABLES = [
    'auth_user', 'auth_group', 'auth_permission', 'django_migrations', 
    'django_content_type', 'django_session', 'django_admin_log',
    'auth_group_permissions', 'auth_user_groups', 'auth_user_user_permissions'
]


def list_tables(request):
    """Вывод списка пользовательских таблиц в базе данных, исключая системные."""
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        all_tables = [row[0] for row in cursor.fetchall()]

    # Исключаем стандартные Django-таблицы
    user_tables = [table for table in all_tables if table not in EXCLUDED_TABLES]

    return render(request, 'db_app/list_tables.html', {'tables': user_tables})


def view_table(request, table_name):
    """Вывод данных из выбранной таблицы с пагинацией и названиями столбцов."""
    with connection.cursor() as cursor:
        # Получаем данные из выбранной таблицы
        cursor.execute(f"SELECT * FROM `{table_name}`;")
        rows = cursor.fetchall()

        # Получаем названия колонок (первый элемент из cursor.description)
        column_names = [desc[0] for desc in cursor.description]

    # Пагинация: 5 записей на страницу
    paginator = Paginator(rows, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'db_app/view_table.html', {
        'table_name': table_name,
        'columns': column_names,  # Передаем названия колонок в шаблон
        'page_obj': page_obj,  # Объект пагинации
    })


def get_model_by_name(table_name):
    # Используем Python reflection, чтобы найти модель по имени
    model_name = ''.join(tmp.capitalize() for tmp in table_name.split('_'))
    try:
        model = globals()[model_name]  # Получаем модель по имени
        return model
    except KeyError:
        raise Http404("Модель не найдена для таблицы: " + table_name, 'model_name:', model_name)


@login_required
def edit_record(request, table_name, key):
    # Получаем модель по имени таблицы
    model = get_model_by_name(table_name)

    print('afasdf', model)
    record = get_object_or_404(model, pk=key)


    # Создаем форму для этой модели
    form_class = modelform_factory(model, exclude=[model._meta.pk.name])
    form = form_class(instance=record)

    if request.method == 'POST':

        form = form_class(request.POST, request.FILES, instance=record)  # Обрабатываем файлы с request.FILES
        
        if form.is_valid():
            form.save()   
            return redirect('db_app:view_table', table_name=table_name)
    
    context = {
        'form': form,
        'table_name': table_name,
        'record': record,
    }
    return render(request, 'db_app/edit_record.html', context)

@login_required
def delete_record(request, table_name, key):
    # Получаем модель по имени таблицы
    model = get_model_by_name(table_name)

    # Определяем запись
    record = model.objects.filter(pk=key).first()

    if not record:
        raise Http404("Запись не найдена")

    # Удаляем запись
    if request.method == 'POST':
        record.delete()
        return redirect('db_app:view_table', table_name=table_name)

    model_from_record = model_to_dict(record)

    # Передаём запись в шаблон для отображения
    return render(request, 'db_app/confirm_delete.html', {
        'record': model_from_record.values(),
        'columns': list(model_from_record.keys()),
        'table_name': table_name
    })


@login_required
def add_record(request, table_name):
    model = get_model_by_name(table_name)
    form_class = modelform_factory(model, exclude=['id'])  # Исключаем поле 'id'
    form = form_class()

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('db_app:view_table', table_name=table_name)

    context = {'form': form, 'table_name': table_name}
    return render(request, 'db_app/add_record.html', context)


def count_bookings(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT CountBookings();")
        bookings_count = cursor.fetchone()[0]

    return render(request, 'db_app/count_bookings.html', {'bookings_count': bookings_count})


def view_bookings(request):
    # Получаем GET параметры
    date_in_min = request.GET.get('date_in_min')
    date_in_max = request.GET.get('date_in_max')
    date_out_min = request.GET.get('date_out_min')
    date_out_max = request.GET.get('date_out_max')

    # Начальный QuerySet
    bookings = Bookings.objects.all()

    # Применяем фильтры
    if date_in_min:
        bookings = bookings.filter(check_in_date__gte=date_in_min)
    if date_in_max:
        bookings = bookings.filter(check_in_date__lte=date_in_max)
    if date_out_min:
        bookings = bookings.filter(check_out_date__gte=date_out_min)
    if date_out_max:
        bookings = bookings.filter(check_out_date__lte=date_out_max)

    # Добавляем пагинацию
    paginator = Paginator(bookings, 6)  # 6 записей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передаем пагинированные записи
    context = {
        'bookings': page_obj
    }
    return render(request, 'db_app/bookings.html', context)

