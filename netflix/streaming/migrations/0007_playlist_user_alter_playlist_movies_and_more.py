# Generated by Django 5.1.3 on 2024-12-10 17:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0006_playlist_series'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='playlist',
            name='movies',
            field=models.ManyToManyField(blank=True, related_name='playlists', to='streaming.movie'),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='name',
            field=models.CharField(default='My Playlist', max_length=100),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='series',
            field=models.ManyToManyField(blank=True, related_name='playlists', to='streaming.series'),
        ),
    ]
