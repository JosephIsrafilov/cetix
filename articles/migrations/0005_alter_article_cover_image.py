from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_article_external_cover_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='cover_image',
            field=models.ImageField(blank=True, upload_to='covers/'),
        ),
    ]
