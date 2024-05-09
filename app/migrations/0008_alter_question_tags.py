# Generated by Django 4.2.7 on 2023-11-14 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_question_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(blank=True, max_length=3, null=True, related_name='questions', to='app.tag'),
        ),
    ]
