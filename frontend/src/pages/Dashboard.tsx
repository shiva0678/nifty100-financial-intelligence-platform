import { useEffect, useMemo, useState } from 'react';
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
import { fetchCompanies, fetchCompanyDetail, fetchCompanyMetrics, fetchCompanyScores } from '../api';
import type { CompanySummary, CompanyDetail, CompanyMetrics, CompanyScores } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

function Dashboard() {
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [selectedTicker, setSelectedTicker] = useState('');
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [metrics, setMetrics] = useState<CompanyMetrics | null>(null);
  const [scores, setScores] = useState<CompanyScores | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    setError(null);

    fetchCompanies(1, 50)
      .then((result) => {
        setCompanies(result.results);
        if (result.results.length > 0) {
          setSelectedTicker(result.results[0].ticker);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedTicker) {
      return;
    }

    setIsLoading(true);
    setError(null);

    Promise.all([
      fetchCompanyDetail(selectedTicker),
      fetchCompanyMetrics(selectedTicker),
      fetchCompanyScores(selectedTicker),
    ])
      .then(([companyDetail, companyMetrics, companyScores]) => {
        setCompany(companyDetail);
        setMetrics(companyMetrics);
        setScores(companyScores);
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [selectedTicker]);

  const years = useMemo(() => {
    return metrics?.metrics.map((item) => item.year.toString()) ?? [];
  }, [metrics]);

  const revenueData = useMemo(() => {
    if (!metrics) return null;
    return {
      labels: years,
      datasets: [
        {
          label: 'Revenue',
          data: metrics.metrics.map((item) => item.sales ?? 0),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139,92,246,0.28)',
          fill: true,
          tension: 0.35,
        },
      ],
    };
  }, [metrics, years]);

  const profitData = useMemo(() => {
    if (!metrics) return null;
    return {
      labels: years,
      datasets: [
        {
          label: 'Net Profit',
          data: metrics.metrics.map((item) => item.net_profit ?? 0),
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.28)',
          fill: true,
          tension: 0.35,
        },
      ],
    };
  }, [metrics, years]);

  const debtData = useMemo(() => {
    if (!company) return null;
    const rows = company.balance_sheets?.sort((a, b) => (a.year ?? 0) - (b.year ?? 0)) ?? [];
    return {
      labels: rows.map((item) => item.year?.toString() ?? ''),
      datasets: [
        {
          label: 'Total Liabilities',
          data: rows.map((item) => item.total_liabilities ?? 0),
          borderColor: '#f97316',
          backgroundColor: 'rgba(249,115,22,0.28)',
          fill: true,
          tension: 0.35,
        },
      ],
    };
  }, [company]);

  const cashFlowData = useMemo(() => {
    if (!company) return null;
    const rows = company.cash_flows?.sort((a, b) => (a.year ?? 0) - (b.year ?? 0)) ?? [];
    return {
      labels: rows.map((item) => item.year?.toString() ?? ''),
      datasets: [
        {
          label: 'Cash Flow',
          data: rows.map((item) => item.net_cash_flow ?? 0),
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56,189,248,0.28)',
          fill: true,
          tension: 0.35,
        },
      ],
    };
  }, [company]);

  const scoreData = useMemo(() => {
    if (!scores) return null;
    const sorted = [...scores.scores].sort((a, b) => a.year - b.year);
    return {
      labels: sorted.map((score) => score.year.toString()),
      datasets: [
        {
          label: 'Health Score',
          data: sorted.map((score) => score.score),
          borderColor: '#a855f7',
          backgroundColor: 'rgba(168,85,247,0.28)',
          fill: true,
          tension: 0.35,
        },
      ],
    };
  }, [scores]);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      tooltip: { mode: 'index' as const, intersect: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: number | string) =>
            typeof value === 'number' ? value.toLocaleString() : value,
        },
      },
    },
  };

  return (
    <section className="space-y-8">
      <div className="rounded-[2rem] border border-slate-800 bg-slate-900/90 p-8 shadow-xl shadow-slate-950/20 sm:p-10">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm uppercase tracking-[0.28em] text-violet-400">Financial dashboard</p>
            <h1 className="mt-3 text-4xl font-semibold text-white">Company performance overview</h1>
            <p className="mt-4 max-w-2xl text-slate-300">
              Explore the key indicators driving revenue, profit, debt, cash flow, and overall health. Use the company selector to view a complete trend analysis in one place.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-800 bg-slate-950/80 px-5 py-4 text-sm text-slate-300">
            <label htmlFor="dashboard-company" className="block text-xs uppercase tracking-[0.24em] text-slate-500">
              Select company
            </label>
            <select
              id="dashboard-company"
              className="mt-3 block w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-white outline-none focus:border-violet-500"
              value={selectedTicker}
              onChange={(event) => setSelectedTicker(event.target.value)}
            >
              {companies.map((item) => (
                <option key={item.ticker} value={item.ticker}>
                  {item.ticker} — {item.company_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-200">
          <p className="text-lg font-semibold">Unable to load dashboard data</p>
          <p className="mt-3 text-sm text-slate-300">{error}</p>
        </div>
      ) : (
        <div className="space-y-8">
          <div className="grid gap-6 xl:grid-cols-2">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
              <h2 className="text-xl font-semibold text-white">Revenue trend</h2>
              <p className="mt-2 text-sm text-slate-400">Annual revenue performance based on reported sales.</p>
              {revenueData ? <Line data={revenueData} options={chartOptions} /> : <p className="mt-6 text-slate-400">No revenue data available.</p>}
            </div>
            <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
              <h2 className="text-xl font-semibold text-white">Profit trend</h2>
              <p className="mt-2 text-sm text-slate-400">Net profit performance for the selected company.</p>
              {profitData ? <Line data={profitData} options={chartOptions} /> : <p className="mt-6 text-slate-400">No profit data available.</p>}
            </div>
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
              <h2 className="text-xl font-semibold text-white">Debt trend</h2>
              <p className="mt-2 text-sm text-slate-400">Liabilities progression tracked from the balance sheet.</p>
              {debtData ? <Line data={debtData} options={chartOptions} /> : <p className="mt-6 text-slate-400">No balance sheet data available.</p>}
            </div>
            <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
              <h2 className="text-xl font-semibold text-white">Cash flow trend</h2>
              <p className="mt-2 text-sm text-slate-400">Annual cash flow movement from operating activities.</p>
              {cashFlowData ? <Line data={cashFlowData} options={chartOptions} /> : <p className="mt-6 text-slate-400">No cash flow data available.</p>}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
            <h2 className="text-xl font-semibold text-white">Health score</h2>
            <p className="mt-2 text-sm text-slate-400">Company financial health score over time.</p>
            {scoreData ? <Line data={scoreData} options={chartOptions} /> : <p className="mt-6 text-slate-400">No health score history available.</p>}
          </div>

          {company ? (
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-100">
                <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Current market position</p>
                <p className="mt-4 text-3xl font-semibold text-white">{company.ticker}</p>
                <p className="mt-2 text-sm text-slate-400">{company.company_name}</p>
              </div>
              <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-100">
                <p className="text-sm uppercase tracking-[0.18em] text-slate-500">ROCE</p>
                <p className="mt-4 text-3xl font-semibold text-white">{company.roce_percentage ?? 'N/A'}%</p>
              </div>
              <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-100">
                <p className="text-sm uppercase tracking-[0.18em] text-slate-500">ROE</p>
                <p className="mt-4 text-3xl font-semibold text-white">{company.roe_percentage ?? 'N/A'}%</p>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

export default Dashboard;
