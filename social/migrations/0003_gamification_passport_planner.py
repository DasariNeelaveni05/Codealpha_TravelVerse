from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_post_hidden_gem_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hidden_gem_score',
            field=models.PositiveSmallIntegerField(default=0, help_text='0-100 community gem score'),
        ),
        migrations.AddField(
            model_name='blog',
            name='budget',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='blog',
            name='itinerary',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='blog',
            name='recommendations',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='progress',
            field=models.PositiveSmallIntegerField(default=0, help_text='0-100 planning progress'),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='status',
            field=models.CharField(
                choices=[
                    ('planned', 'Planned'),
                    ('in_progress', 'In Progress'),
                    ('visited', 'Visited'),
                ],
                default='planned',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='bucketlist',
            name='travel_goal',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='passportstamp',
            name='continent',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Unknown'),
                    ('Africa', 'Africa'),
                    ('Asia', 'Asia'),
                    ('Europe', 'Europe'),
                    ('North America', 'North America'),
                    ('South America', 'South America'),
                    ('Oceania', 'Oceania'),
                    ('Antarctica', 'Antarctica'),
                ],
                default='',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='passportstamp',
            name='stamp_label',
            field=models.CharField(blank=True, help_text='Passport stamp title', max_length=120),
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(
                choices=[
                    ('beach', 'Beaches'),
                    ('mountain', 'Mountains'),
                    ('adventure', 'Adventure'),
                    ('historical', 'Historical Places'),
                    ('food', 'Food Destinations'),
                    ('nature', 'Nature'),
                    ('island', 'Islands'),
                    ('budget', 'Budget Travel'),
                    ('city', 'City'),
                    ('forest', 'Forest'),
                    ('desert', 'Desert'),
                    ('cultural', 'Cultural'),
                    ('other', 'Other'),
                ],
                default='other',
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50)),
                ('unlocked_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='achievements', to='auth.user')),
            ],
            options={
                'unique_together': {('user', 'key')},
            },
        ),
    ]
