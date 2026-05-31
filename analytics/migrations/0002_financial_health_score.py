from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialHealthScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.SmallIntegerField(verbose_name='Fiscal Year')),
                ('score', models.IntegerField(blank=True, null=True, verbose_name='Health Score')),
                ('label', models.CharField(blank=True, max_length=64, null=True, verbose_name='Score Label')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='health_scores', to='companies.company', verbose_name='Company')),
            ],
            options={
                'db_table': 'financial_health_score',
                'verbose_name': 'Financial Health Score',
                'verbose_name_plural': 'Financial Health Scores',
                'ordering': ['company', '-year'],
                'indexes': [
                    models.Index(fields=['company', 'year'], name='idx_health_score_company_year'),
                    models.Index(fields=['year'], name='idx_health_score_year'),
                ],
                'unique_together': {('company', 'year')},
            },
        ),
    ]
