# Generated by Django 5.1.3 on 2024-12-03 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetapp', '0004_subexpense'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField()),
                ('action', models.CharField(choices=[('create', 'Created'), ('update', 'Updated'), ('delete', 'Deleted')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]