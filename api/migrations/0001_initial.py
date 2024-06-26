# Generated by Django 5.0.3 on 2024-06-09 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('is_active', models.BooleanField(default=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('price', models.IntegerField(blank=True, null=True)),
                ('category', models.CharField(blank=True, choices=[('macbook', 'MacBook'), ('iphone', 'iPhone'), ('ipad', 'iPad'), ('watch', 'Watch'), ('airpods', 'AirPods'), ('tvandhome', 'TvAndHome'), ('others', 'Others')], max_length=50, null=True)),
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
            ],
        ),
    ]
