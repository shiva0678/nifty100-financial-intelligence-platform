import { useEffect, useMemo, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchCompanyDetail, fetchCompanyMetrics, fetchCompanyScores } from '../api';
import type { CompanyDetail, CompanyMetrics, CompanyScores } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

function CompanyDetail() {
  const { symbol } = useParams<{ symbol: string }>();
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [metrics, setMetrics] = useState<CompanyMetrics | null>(null);
  const [scores, setScores] = useState<CompanyScores | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) {
      setError('Missing company symbol in route.');
      return;
    }

    setIsLoading(true);
    setError(null);

    Promise.all([
      fetchCompanyDetail(symbol),
      fetchCompanyMetrics(symbol),
      fetchCompanyScores(symbol),
    ])
      .then(([detail, metricsResponse, scoreResponse]) => {
        setCompany(detail);
        setMetrics(metricsResponse);
        setScores(scoreResponse);
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [symbol]);

  const years = useMemo(() => {
    return metrics?.metrics.map((item) => item.year.toString()) ?? [];
  }, [metrics]);

  const financialDataset = useMemo(() => {
    if (!metrics) return null;
    return {
      labels: years,
      datasets: [
        {
          label: 'Sales',
          data: metrics.metrics.map((item) => item.sales ?? 0),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139,92,246,0.32)',
          fill: true,
        },
        {
          label: 'Net Profit',
          data: metrics.metrics.map((item) => item.net_profit ?? 0),
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.24)',
          fill: true,
        },
      ],
    };
  }, [metrics, years]);

  const scoreDataset = useMemo(() => {
    if (!scores) return null;
    return {
      labels: scores.scores.map((item) => item.year.toString()),
      datasets: [
        {
          label: 'Health Score',
          data: scores.scores.map((item) => item.score),
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56,189,248,0.28)',
          fill: true,
          tension: 0.3,
        },
      ],
    };
  }, [scores]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error || !company) {
    return (
      <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-slate-100">
        <p className="text-lg font-semibold">Company details could not be loaded.</p>
        <p className="mt-3 text-sm text-slate-300">{error ?? 'Please verify the ticker and try again.'}</p>
        <Link to="/companies" className="mt-6 inline-flex rounded-full bg-slate-700 px-5 py-3 text-sm text-white hover:bg-slate-600">
          Return to companies
        </Link>
      </div>
    );
  }

  return (
    <section className="space-y-8">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 sm:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-violet-400">Company details</p>
            <h1 className="mt-3 text-3xl font-semibold text-white">{company.company_name}</h1>
            <p className="mt-2 max-w-2xl text-slate-300">{company.about_company ?? 'No company description available.'}</p>
          </div>
          <div className="space-y-3 rounded-3xl border border-slate-800 bg-slate-950/90 p-5">
            <p className="text-sm text-slate-400">Ticker</p>
            <p className="text-2xl font-semibold text-white">{company.ticker}</p>
            {company.website ? (
              <a
                href={company.website}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-violet-300 hover:text-violet-100"
              >
                Visit website
              </a>
            ) : null}
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-3xl bg-slate-950/90 p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">ROCE</p>
            <p className="mt-3 text-3xl font-semibold text-white">{company.roce_percentage ?? 'N/A'}%</p>
          </div>
          <div className="rounded-3xl bg-slate-950/90 p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">ROE</p>
            <p className="mt-3 text-3xl font-semibold text-white">{company.roe_percentage ?? 'N/A'}%</p>
          </div>
          <div className="rounded-3xl bg-slate-950/90 p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Book value</p>
            <p className="mt-3 text-3xl font-semibold text-white">
              {company.book_value != null ? `₹${company.book_value.toLocaleString()}` : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">Revenue & Net Profit</h2>
              <p className="mt-1 text-sm text-slate-400">Year-over-year performance from the financial metrics endpoint.</p>
            </div>
          </div>
          {financialDataset ? (
            <Line
              data={financialDataset}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: false, text: 'Revenue & Net Profit' },
                },
              }}
            />
          ) : (
            <p className="text-slate-400">No metrics available yet.</p>
          )}
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-white">Health score history</h2>
            <p className="mt-1 text-sm text-slate-400">Historic score trends derived from the analytics pipeline.</p>
          </div>
          {scoreDataset ? (
            <Line
              data={scoreDataset}
              options={{
                responsive: true,
                scales: {
                  y: { suggestedMin: 0, suggestedMax: 100 },
                },
                plugins: {
                  legend: { position: 'top' },
                },
              }}
            />
          ) : (
            <p className="text-slate-400">Score data is not available yet.</p>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <h2 className="text-xl font-semibold text-white">Analysis summary</h2>
          <dl className="mt-5 grid gap-4 text-slate-300">
            <div className="rounded-3xl bg-slate-950/80 p-4">
              <dt className="text-sm text-slate-500">Compounded sales growth</dt>
              <dd className="mt-2 text-lg font-semibold text-white">
                {company.analysis?.compounded_sales_growth ?? 'N/A'}%
              </dd>
            </div>
            <div className="rounded-3xl bg-slate-950/80 p-4">
              <dt className="text-sm text-slate-500">Compounded profit growth</dt>
              <dd className="mt-2 text-lg font-semibold text-white">
                {company.analysis?.compounded_profit_growth ?? 'N/A'}%
              </dd>
            </div>
            <div className="rounded-3xl bg-slate-950/80 p-4">
              <dt className="text-sm text-slate-500">Stock price CAGR</dt>
              <dd className="mt-2 text-lg font-semibold text-white">
                {company.analysis?.stock_price_cagr ?? 'N/A'}%
              </dd>
            </div>
          </dl>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <h2 className="text-xl font-semibold text-white">Pros & cons</h2>
          <div className="mt-5 space-y-5 text-slate-300">
            <div className="rounded-3xl bg-slate-950/80 p-5">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Pros</h3>
              <p className="mt-3 leading-7">{company.pros_cons?.pros ?? 'No pros available.'}</p>
            </div>
            <div className="rounded-3xl bg-slate-950/80 p-5">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Cons</h3>
              <p className="mt-3 leading-7">{company.pros_cons?.cons ?? 'No cons available.'}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default CompanyDetail;
