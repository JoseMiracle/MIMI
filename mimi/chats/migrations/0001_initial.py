# Generated by Django 5.0 on 2024-01-31 06:55

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
            name='Room',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('room_creator_id', models.CharField(max_length=250)),
                ('room_name', models.CharField(max_length=100, unique=True)),
                ('number_of_persons', models.IntegerField(default=100)),
                ('is_public', models.BooleanField(default=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('edit_count', models.IntegerField(default=0)),
                ('message', models.TextField()),
                ('receiver', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='receiver_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='sender_mesages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JoinRoomRequests',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('room_request', models.CharField(choices=[(0, 'PENDING'), (1, 'ACCEPTED')], default=0, max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_room_request', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='chats.room')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RoomMembers',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chats.room')),
                ('room_members', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_room_member', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
