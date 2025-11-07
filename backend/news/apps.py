from django.apps import AppConfig
from django.db.utils import OperationalError

# class NewsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'news'

    # def ready(self):
    #     from .models import IndiaNews
    #     from .Webscrapers.India import fetch_latest_news

    #     try:
            
    #             titles, links = fetch_latest_news()
    #             IndiaNews.objects.all().delete()

    #             for t, l in zip(titles, links):
    #                 IndiaNews.objects.create(
    #                     headline={ t},
    #                     link={ l}
    #                 )
    #             print(f"[✔] Inserted {len(titles)} NDTV headlines into the database.")
    #     except OperationalError:
    #         # This prevents Django startup crashes during migrations
    #         pass
    #     except Exception as e:
    #         print(f"[✗] Error in NewsConfig.ready(): {e}")
