from django.urls import reverse
from rest_framework.test import APITestCase

from companies.models import Company, ProfitAndLoss
from analytics.models import FinancialHealthScore


class ApiIntegrationTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            ticker='TST',
            company_name='Test Corporation',
        )

        ProfitAndLoss.objects.create(
            company=self.company,
            year=2024,
            sales=1200000,
            net_profit=220000,
        )

        FinancialHealthScore.objects.create(
            company=self.company,
            year=2024,
            score=82,
            label='Excellent',
        )

    def test_companies_list_returns_results(self):
        url = reverse('api:companies-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_company_detail_returns_full_profile(self):
        url = reverse('api:company-detail', kwargs={'symbol': self.company.ticker})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['ticker'], self.company.ticker)
        self.assertEqual(response.data['company_name'], self.company.company_name)

    def test_company_score_returns_health_history(self):
        url = reverse('api:company-score', kwargs={'symbol': self.company.ticker})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['company'], self.company.ticker)
        self.assertTrue(response.data['scores'])
        self.assertEqual(response.data['scores'][0]['score'], 82)

    def test_company_insights_fallback_returns_pros_cons(self):
        url = reverse('api:company-insights', kwargs={'symbol': self.company.ticker})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['company'], self.company.ticker)
        self.assertIn('pros', response.data)
        self.assertIn('cons', response.data)
