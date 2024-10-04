# Generated by Django 5.1.1 on 2024-09-26 07:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('running', 'Running'), ('cycling', 'Cycling'), ('weightlifting', 'Weight Lifting')], max_length=50)),
                ('duration', models.PositiveIntegerField(help_text='Duration in minutes')),
                ('distance', models.FloatField(blank=True, help_text='Distance in kilometers', null=True)),
                ('calories_burned', models.PositiveIntegerField(help_text='calories burned')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activties', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
