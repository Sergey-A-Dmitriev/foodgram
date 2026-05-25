import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class BaseLoadJSONCommand(BaseCommand):
    """Базовый загрузчик JSON фикстур."""

    model = None
    file_name = None
    fields = None

    def get_file_path(self):
        return Path(settings.BASE_DIR).parent / 'data' / self.file_name

    def handle(self, *args, **options):
        try:
            with open(self.get_file_path(), encoding='utf-8') as file:
                data = json.load(file)
            objects = [
                self.model(**{
                    field: item[field]
                    for field in self.fields})
                for item in data]
            created = self.model.objects.bulk_create(objects)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Фикстура "{self.file_name}" загружена. '
                    f'Создано записей: {len(created)}'))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f'Ошибка загрузки {self.file_name}: {str(e)}'))
