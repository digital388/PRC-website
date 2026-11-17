from django.db import migrations, models


def classify_by_role(apps, schema_editor):
    """Executive is for director roles; everyone else who isn't an advisor or fellow is Staff."""
    TeamMember = apps.get_model('website', 'TeamMember')
    for member in TeamMember.objects.all():
        role = (member.role_en or '').lower()
        if 'advisor' in role or 'adviser' in role:
            category = 'advisor'
        elif 'fellow' in role:
            category = 'research_fellow'
        elif 'executive' in role or 'director' in role:
            category = 'executive'
        else:
            category = 'staff'
        if member.category != category:
            member.category = category
            member.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_teammember_category_by_fellow_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='category',
            field=models.CharField(choices=[('executive', 'Executive'), ('advisor', 'Advisor'), ('research_fellow', 'Research Fellow'), ('staff', 'Staff')], db_index=True, default='executive', max_length=20),
        ),
        migrations.RunPython(classify_by_role, migrations.RunPython.noop),
    ]
