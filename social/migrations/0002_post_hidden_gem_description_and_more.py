# Generated migration for TravelVerse extensions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hidden_gem_description',
            field=models.TextField(
                blank=True,
                help_text='Why is this place a hidden gem?',
                max_length=1500,
            ),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='planned_date',
            field=models.DateField(blank=True, help_text='When you plan to visit', null=True),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='priority',
            field=models.CharField(
                blank=True,
                choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                default='medium',
                max_length=20,
            ),
        ),
    ]
