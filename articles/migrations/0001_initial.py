<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('cover_image', models.ImageField(upload_to='covers/')),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending Review'), ('published', 'Published'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('last_moderated_at', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to=settings.AUTH_USER_MODEL)),
                ('last_moderated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderated_articles', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles', to='articles.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ArticleRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='articles.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('article', 'user')},
            },
        ),
        migrations.CreateModel(
            name='ArticleReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='articles.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_reactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('article', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='articles.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('article', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['status'], name='articles_ar_status_edb746_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['-published_at'], name='articles_ar_publish_c1a2fc_idx'),
        ),
    ]
