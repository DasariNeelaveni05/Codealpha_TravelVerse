from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_gamification_passport_planner'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='budget_amount',
            field=models.PositiveIntegerField(blank=True, help_text='Trip budget in USD', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='cover_theme',
            field=models.CharField(blank=True, help_text='Placeholder image theme key', max_length=30),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='reminder_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='TravelCompanion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=200)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, max_length=800)),
                ('budget_range', models.CharField(blank=True, max_length=80)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='companion_trips', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
