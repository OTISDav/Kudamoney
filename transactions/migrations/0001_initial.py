# Generated by Django 5.2.1 on 2025-05-20 22:41

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscountCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        default=uuid.uuid4,
                        max_length=20,
                        unique=True,
                        verbose_name="Code de réduction",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Description"
                    ),
                ),
                (
                    "discount_percentage",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        verbose_name="Pourcentage de réduction",
                    ),
                ),
                (
                    "fixed_amount_discount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Montant de réduction fixe",
                    ),
                ),
                (
                    "max_uses",
                    models.IntegerField(
                        default=1, verbose_name="Nombre maximum d'utilisations"
                    ),
                ),
                (
                    "uses_count",
                    models.IntegerField(
                        default=0, verbose_name="Nombre d'utilisations actuelles"
                    ),
                ),
                (
                    "valid_from",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Valide à partir de"
                    ),
                ),
                (
                    "valid_until",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Valide jusqu'à"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Créé par",
                    ),
                ),
            ],
            options={
                "verbose_name": "Code de Réduction",
                "verbose_name_plural": "Codes de Réduction",
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Montant"
                    ),
                ),
                (
                    "final_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Montant final après réduction",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "En attente"),
                            ("success", "Réussie"),
                            ("failed", "Échouée"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date de création"
                    ),
                ),
                (
                    "discount_code_used",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="transactions.discountcode",
                        verbose_name="Code de réduction utilisé",
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_transactions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Bénéficiaire",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_transactions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Expéditeur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
            },
        ),
    ]
