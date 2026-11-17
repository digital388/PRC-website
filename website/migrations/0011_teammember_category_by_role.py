from django.db import migrations


def classify_by_role(apps, schema_editor):
    """Distribute members into sections based on their role title."""
    TeamMember = apps.get_model('website', 'TeamMember')
    for member in TeamMember.objects.all():
        role = (member.role_en or '').lower()
        if 'advisor' in role or 'adviser' in role:
            category = 'advisor'
        elif 'research' in role:
            category = 'research_fellow'
        else:
            category = 'executive'
        if member.category != category:
            member.category = category
            member.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_teammember_category'),
    ]

    operations = [
        migrations.RunPython(classify_by_role, migrations.RunPython.noop),
    ]
