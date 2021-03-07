from django.db import models

# Create your models here.
class {{ ModelName }} (models.Model):
    {% for key, value in collumns.items() %}
    {{key}} = {{value}}
    {% endfor %}