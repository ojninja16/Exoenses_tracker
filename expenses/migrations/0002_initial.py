# Generated by Django 4.2.7 on 2024-10-21 13:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensesplit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_splits', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='expense',
            name='paid_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paid_expenses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='expensesplit',
            unique_together={('expense', 'user')},
        ),
    ]
