# Generated by Django 5.1.3 on 2025-03-13 07:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("budgetapp", "0005_subexpense_is_return"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Goal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("current_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("start_date", models.DateField()),
                ("target_date", models.DateField(blank=True, null=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("vacation", "Vacation"),
                            ("emergency", "Emergency Fund"),
                            ("education", "Education"),
                            ("housing", "Housing"),
                            ("vehicle", "Vehicle"),
                            ("electronics", "Electronics"),
                            ("medical", "Medical Expense"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[("high", "High"), ("medium", "Medium"), ("low", "Low")],
                        default="medium",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="goals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GoalContribution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date", models.DateField()),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("direct", "Direct Contribution"),
                            ("savings", "From Savings"),
                            ("expense_reduction", "Expense Reduction"),
                            ("income", "Extra Income"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "goal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contributions",
                        to="budgetapp.goal",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
        migrations.AddIndex(
            model_name="goal",
            index=models.Index(fields=["user"], name="budgetapp_g_user_id_da9968_idx"),
        ),
        migrations.AddIndex(
            model_name="goal",
            index=models.Index(fields=["category"], name="budgetapp_g_categor_4ff8df_idx"),
        ),
        migrations.AddIndex(
            model_name="goal",
            index=models.Index(fields=["is_active"], name="budgetapp_g_is_acti_3ae6ef_idx"),
        ),
        migrations.AddIndex(
            model_name="goalcontribution",
            index=models.Index(fields=["goal"], name="budgetapp_g_goal_id_5f0696_idx"),
        ),
        migrations.AddIndex(
            model_name="goalcontribution",
            index=models.Index(fields=["date"], name="budgetapp_g_date_4ab4fc_idx"),
        ),
    ]
