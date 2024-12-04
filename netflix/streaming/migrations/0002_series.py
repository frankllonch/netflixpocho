# Generated by Django 5.1.3 on 2024-12-03 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('release_date', models.DateField()),
                ('genre', models.CharField(max_length=100)),
                ('rating', models.FloatField()),
                ('poster_path', models.URLField()),
            ],
        ),
    ]