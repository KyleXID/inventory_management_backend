# Generated by Django 4.2.7 on 2023-11-26 17:29

from django.db import migrations


def add_dummy_items(apps, schema_editor):
    Item = apps.get_model('inventory', 'Item')

    name_list = ["감자", "고구마", "브로콜리", "단호박", "양상추", "양배추"]

    item_list = [
        Item(
            name=name
        ) for name in name_list
    ]
    Item.objects.bulk_create(item_list)


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_dummy_items,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
