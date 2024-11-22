from django.contrib import admin
from .models import Category, Request

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Category, CategoryAdmin)

class RequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'user', 'created_at']  # Добавим статус в список
    list_filter = ['status', 'category']  # Фильтрация по статусу и категории
    actions = ['set_in_progress', 'set_completed']

    def set_in_progress(self, request, queryset):
        queryset.update(status='in_progress')  # Меняем статус на "Принято в работу"
    set_in_progress.short_description = "Отметить как 'Принято в работу'"

    def set_completed(self, request, queryset):
        queryset.update(status='completed')  # Меняем статус на "Выполнено"
    set_completed.short_description = "Отметить как 'Выполнено'"

admin.site.register(Request, RequestAdmin)
