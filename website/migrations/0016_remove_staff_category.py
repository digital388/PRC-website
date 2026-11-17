from django.db import migrations, models


def staff_to_executive(apps, schema_editor):
    TeamMember = apps.get_model('website', 'TeamMember')
    TeamMember.objects.filter(category='staff').update(category='executive')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_alter_blogpost_is_hidden_alter_boardmember_is_hidden_and_more'),
    ]

    operations = [
        migrations.RunPython(staff_to_executive, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='teammember',
            name='category',
            field=models.CharField(choices=[('executive', 'Executive'), ('advisor', 'Advisor'), ('research_fellow', 'Research Fellow')], db_index=True, default='executive', max_length=20),
        ),
    ]
