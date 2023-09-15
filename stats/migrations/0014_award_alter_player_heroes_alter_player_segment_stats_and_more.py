# Generated by Django 4.2.3 on 2023-09-15 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0013_alter_match_match_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.AlterField(
            model_name='player',
            name='heroes',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='segment_stats',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='stats',
            field=models.JSONField(null=True),
        ),
    ]
