from django.db import migrations, models
import django.utils.timezone


def populate_task_timestamps(apps, schema_editor):
    Task = apps.get_model('engine', 'Task')
    Message = apps.get_model('engine', 'Message')
    for task in Task.objects.all():
        changed = False
        if not task.created:
            task.created = task.workflow.created
            changed = True
        if not task.finished:
            last_msg = Message.objects.filter(task=task).order_by('-timestamp').first()
            if last_msg:
                task.finished = last_msg.timestamp
                changed = True
        if changed:
            task.save(update_fields=['created', 'finished'])


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='finished',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(populate_task_timestamps, migrations.RunPython.noop),
    ]
