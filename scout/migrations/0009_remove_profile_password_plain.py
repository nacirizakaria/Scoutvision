from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scout', '0008_alter_playerapproval_analyst_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='password_plain',
        ),
    ]
