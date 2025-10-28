from django.db import migrations


CATEGORIES = [
    ("Backend", "backend"),
    ("Frontend", "frontend"),
    ("AI", "ai"),
    ("Cyber Security", "cyber-security"),
    ("Cyber Sport", "cyber-sport"),
    ("Game Development", "game-development"),
]


def create_categories(apps, schema_editor):
    Category = apps.get_model("articles", "Category")
    for name, slug in CATEGORIES:
        Category.objects.get_or_create(name=name, defaults={"slug": slug})


def delete_categories(apps, schema_editor):
    Category = apps.get_model("articles", "Category")
    Category.objects.filter(name__in=[name for name, _ in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_categories, delete_categories),
    ]
