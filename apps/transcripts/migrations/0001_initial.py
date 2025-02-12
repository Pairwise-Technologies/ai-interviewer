# Generated by Django 5.0.3 on 2025-02-12 22:51

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
        ('profiles', '0003_remove_profile_user_talentprofile_delete_employee_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transcripts', to='profiles.talentprofile')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transcripts', to='jobs.job')),
            ],
        ),
    ]
