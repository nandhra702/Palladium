from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
            from .models import IndiaNews

            # Example: Add a news item if table is empty
            if not IndiaNews.objects.exists():
                IndiaNews.objects.create(
                    headline={"title": "Trial1_done", "language": "en"},
                    link={"url": "https://example.com", "source": "test"}
                )