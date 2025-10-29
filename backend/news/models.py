
from django.db import models

class IndiaNews(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    headline = models.JSONField(null=True, blank=True)
    link = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'India_news'  # Match your exact table name
        managed = False  # Important: tells Django not to manage this table

    def __str__(self):
        return f"News {self.id}"