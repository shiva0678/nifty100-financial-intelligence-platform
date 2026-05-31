import { useEffect, useMemo, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { fetchCompanies, fetchCompanyDetail, fetchCompanyMetrics, fetchCompanyScores } from '../api';
import type { CompanySummary } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function safeNumber(v: any) {
  if (v === null || v === undefined) return NaN;
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : NaN;
}

function formatCurrency(value: number) {
  return Number.isFinite(value) ? `₹${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : 'N/A';
}

function formatPercent(value: number) {
  return Number.isFinite(value) ? `${value.toFixed(2)}%` : 'N/A';
}

function formatRatio(value: number) {
  return Number.isFinite(value) ? value.toFixed(2) : 'N/A';
}

function computeDebtEquity(balanceSheets: any[] | undefined) {
  if (!balanceSheets || balanceSheets.length === 0) return NaN;
  // use the latest year (highest year number)
  const latest = [...balanceSheets].sort((a, b) => (b.year ?? 0) - (a.year ?? 0))[0];
  const totalLiabilities = safeNumber(latest.total_liabilities);
  const equity = safeNumber((latest.equity_capital ?? 0)) + safeNumber((latest.reserves ?? 0));
  if (!Number.isFinite(totalLiabilities) || !Number.isFinite(equity) || equity === 0) return NaN;
  return totalLiabilities / equity;
}

function computeHealthScoreFromDetail(detail: any, metricsResp: any) {
  const latestMetrics = (metricsResp.metrics ?? []).sort((a: any, b: any) => (b.year ?? 0) - (a.year ?? 0));
  const latest = latestMetrics[0] ?? {};
  const previous = latestMetrics[1] ?? {};

  const latestSales = safeNumber(latest.sales);
  const previousSales = safeNumber(previous.sales);
  const latestProfit = safeNumber(latest.net_profit ?? (latest as any).profit_before_tax ?? 0);
  const previousProfit = safeNumber(previous.net_profit ?? (previous as any).profit_before_tax ?? 0);

  const revenueGrowth = previousSales > 0 ? (latestSales - previousSales) / previousSales : 0;
  const profitGrowth = previousProfit > 0 ? (latestProfit - previousProfit) / previousProfit : 0;
  const roe = safeNumber(detail.roe_percentage ?? detail.roce_percentage ?? 0);
  const debtEquity = computeDebtEquity(detail.balance_sheets);

  const scoreParts = [
    revenueGrowth >= 0.2 ? 20 : revenueGrowth >= 0.1 ? 10 : 0,
    profitGrowth >= 0.2 ? 20 : profitGrowth >= 0.1 ? 10 : 0,
    roe >= 15 ? 20 : roe >= 10 ? 10 : 0,
    debtEquity <= 0.5 ? 20 : debtEquity <= 1.0 ? 10 : 0,
    latestProfit > 0 ? 20 : 0,
  ];

  const score = scoreParts.reduce((sum, part) => sum + part, 0);
  return Math.min(100, Math.max(0, score));
}

function Compare() {
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [leftTicker, setLeftTicker] = useState('');
  const [rightTicker, setRightTicker] = useState('');
  const [leftData, setLeftData] = useState<any | null>(null);
  const [rightData, setRightData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const getFallbackHealthScore = (ticker: string): number | null => {
    const company = companies.find((item) => item.ticker.toUpperCase() === ticker.toUpperCase());
    return company?.health_score ?? null;
  };

  useEffect(() => {
    setIsLoading(true);
    fetchCompanies(1, 200)
      .then((result) => {
        setCompanies(result.results);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    // when a ticker is selected, load its detail/metrics/score
    async function loadFor(ticker: string, setter: (v: any) => void) {
      if (!ticker) {
        setter(null);
        return;
      }
      try {
        setter({ loading: true });
        const [detail, metricsResp, scoresResp] = await Promise.all([
          fetchCompanyDetail(ticker),
          fetchCompanyMetrics(ticker),
          fetchCompanyScores(ticker),
        ]);

        const latestPl = (metricsResp.metrics ?? []).sort((a: any, b: any) => (b.year ?? 0) - (a.year ?? 0))[0] ?? {};
        const revenue = safeNumber(latestPl.sales);
        const profit = safeNumber((latestPl as any).net_profit ?? (latestPl as any).profit_before_tax ?? 0);
        const roe = safeNumber(detail.roe_percentage ?? detail.roce_percentage ?? 0);
        const debtEquity = computeDebtEquity(detail.balance_sheets);
        const latestScore = (scoresResp.scores ?? []).sort((a: any, b: any) => (b.year ?? 0) - (a.year ?? 0))[0];
        const scoreFromHistory = latestScore ? safeNumber(latestScore.score) : NaN;
        const fallbackScore = safeNumber(getFallbackHealthScore(ticker));
        const computedScore = computeHealthScoreFromDetail(detail, metricsResp);
        const healthScore = Number.isFinite(scoreFromHistory)
          ? scoreFromHistory
          : Number.isFinite(fallbackScore)
          ? fallbackScore
          : computedScore;

        setter({
          detail,
          revenue,
          profit,
          roe,
          debtEquity,
          healthScore,
        });
      } catch (err: any) {
        setter({ error: err?.message ?? String(err) });
      }
    }

    loadFor(leftTicker, setLeftData);
  }, [leftTicker, companies]);

  useEffect(() => {
    async function loadFor(ticker: string, setter: (v: any) => void) {
      if (!ticker) {
        setter(null);
        return;
      }
      try {
        setter({ loading: true });
        const [detail, metricsResp, scoresResp] = await Promise.all([
          fetchCompanyDetail(ticker),
          fetchCompanyMetrics(ticker),
          fetchCompanyScores(ticker),
        ]);

        const latestPl = (metricsResp.metrics ?? []).sort((a: any, b: any) => (b.year ?? 0) - (a.year ?? 0))[0] ?? {};
        const revenue = safeNumber(latestPl.sales);
        const profit = safeNumber((latestPl as any).net_profit ?? (latestPl as any).profit_before_tax ?? 0);
        const roe = safeNumber(detail.roe_percentage ?? detail.roce_percentage ?? 0);
        const debtEquity = computeDebtEquity(detail.balance_sheets);
        const latestScore = (scoresResp.scores ?? []).sort((a: any, b: any) => (b.year ?? 0) - (a.year ?? 0))[0];
        const scoreFromHistory = latestScore ? safeNumber(latestScore.score) : NaN;
        const fallbackScore = safeNumber(getFallbackHealthScore(ticker));
        const computedScore = computeHealthScoreFromDetail(detail, metricsResp);
        const healthScore = Number.isFinite(scoreFromHistory)
          ? scoreFromHistory
          : Number.isFinite(fallbackScore)
          ? fallbackScore
          : computedScore;

        setter({
          detail,
          revenue,
          profit,
          roe,
          debtEquity,
          healthScore,
        });
      } catch (err: any) {
        setter({ error: err?.message ?? String(err) });
      }
    }

    loadFor(rightTicker, setRightData);
  }, [rightTicker, companies]);

  const chartData = useMemo(() => {
    if (!leftData || !rightData) return null;
    if (leftData.loading || rightData.loading) return null;
    if (leftData.error || rightData.error) return null;
    if (!leftData.detail || !rightData.detail) return null;

    const labels = ['Revenue', 'Profit'];
    const leftValues = [leftData.revenue, leftData.profit].map((v: any) => (Number.isFinite(v) ? v : 0));
    const rightValues = [rightData.revenue, rightData.profit].map((v: any) => (Number.isFinite(v) ? v : 0));

    return {
      labels,
      datasets: [
        {
          label: leftData.detail.company_name ?? 'Company 1',
          data: leftValues,
          backgroundColor: 'rgba(139,92,246,0.75)',
        },
        {
          label: rightData.detail.company_name ?? 'Company 2',
          data: rightValues,
          backgroundColor: 'rgba(34,197,94,0.75)',
        },
      ],
    };
  }, [leftData, rightData]);

  const secondaryChartData = useMemo(() => {
    if (!leftData || !rightData) return null;
    if (leftData.loading || rightData.loading) return null;
    if (leftData.error || rightData.error) return null;
    if (!leftData.detail || !rightData.detail) return null;

    const labels = ['ROE (%)', 'Debt/Equity', 'Health Score'];
    const leftValues = [leftData.roe, leftData.debtEquity, leftData.healthScore].map((v: any) => (Number.isFinite(v) ? v : 0));
    const rightValues = [rightData.roe, rightData.debtEquity, rightData.healthScore].map((v: any) => (Number.isFinite(v) ? v : 0));

    return {
      labels,
      datasets: [
        {
          label: leftData.detail.company_name ?? 'Company 1',
          data: leftValues,
          backgroundColor: 'rgba(139,92,246,0.75)',
        },
        {
          label: rightData.detail.company_name ?? 'Company 2',
          data: rightValues,
          backgroundColor: 'rgba(34,197,94,0.75)',
        },
      ],
    };
  }, [leftData, rightData]);

  const comparisonDetails = useMemo(() => {
    if (!leftData || !rightData) return [];
    return [
      { label: 'Revenue', left: formatCurrency(leftData.revenue), right: formatCurrency(rightData.revenue) },
      { label: 'Profit', left: formatCurrency(leftData.profit), right: formatCurrency(rightData.profit) },
      { label: 'ROE', left: formatPercent(leftData.roe), right: formatPercent(rightData.roe) },
      { label: 'Debt/Equity', left: formatRatio(leftData.debtEquity), right: formatRatio(rightData.debtEquity) },
      { label: 'Health Score', left: formatRatio(leftData.healthScore), right: formatRatio(rightData.healthScore) },
    ];
  }, [leftData, rightData]);

  const isBusy = isLoading || (leftData && leftData.loading) || (rightData && rightData.loading);

  return (
    <section className="space-y-8">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20 sm:p-8">
        <h1 className="text-3xl font-semibold text-white">Compare Companies</h1>
        <p className="mt-3 text-slate-400">Select two companies to compare Revenue, Profit, ROE, Debt/Equity and Health Score.</p>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          {['left', 'right'].map((position) => {
            const selectValue = position === 'left' ? leftTicker : rightTicker;
            const setValue = position === 'left' ? setLeftTicker : setRightTicker;
            return (
              <label key={position} className="space-y-3 rounded-3xl border border-slate-800 bg-slate-950/80 p-5">
                <span className="block text-sm font-semibold text-white">{position === 'left' ? 'First company' : 'Second company'}</span>
                <select
                  value={selectValue}
                  onChange={(event) => setValue(event.target.value)}
                  className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-slate-100 outline-none transition focus:border-violet-500"
                >
                  <option value="">Select a company</option>
                  {companies.map((company) => (
                    <option key={company.ticker} value={company.ticker}>
                      {company.ticker} — {company.company_name}
                    </option>
                  ))}
                </select>
              </label>
            );
          })}
        </div>
      </div>

      {isBusy ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 text-slate-100">
          <p className="text-lg font-semibold">Unable to load company list</p>
          <p className="mt-2 text-sm text-slate-300">{error}</p>
        </div>
      ) : !leftData || !rightData ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-300">
          Select two companies to compare.
        </div>
      ) : (leftData.error || rightData.error) ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 text-slate-100">
          <p className="text-lg font-semibold">Error loading company data</p>
          <p className="mt-2 text-sm text-slate-300">{leftData.error ?? rightData.error}</p>
        </div>
      ) : (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/20">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">Comparison chart</h2>
              <p className="mt-2 text-slate-400">Comparing the two selected companies across key financial indicators.</p>
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-5 mb-6">
            {comparisonDetails.map((item) => (
              <div key={item.label} className="rounded-3xl border border-slate-800 bg-slate-950/80 p-5">
                <p className="text-sm uppercase tracking-[0.18em] text-slate-500">{item.label}</p>
                <div className="mt-3 flex flex-col gap-2 text-sm text-slate-300">
                  <p>
                    <span className="font-semibold text-white">{leftData?.detail?.company_name ?? 'Company 1'}:</span> {item.left}
                  </p>
                  <p>
                    <span className="font-semibold text-white">{rightData?.detail?.company_name ?? 'Company 2'}:</span> {item.right}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {chartData ? (
            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4">Revenue & Profit</h3>
              <Bar
                data={chartData}
                options={{
                  responsive: true,
                  plugins: {
                    tooltip: { mode: 'index', intersect: false },
                    legend: { position: 'top' },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        callback: (value) => (typeof value === 'number' ? `₹${value.toLocaleString()}` : value),
                      },
                    },
                  },
                }}
              />
            </div>
          ) : null}

          {secondaryChartData ? (
            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">ROE, Debt/Equity & Health Score</h3>
              <Bar
                data={secondaryChartData}
                options={{
                  responsive: true,
                  plugins: {
                    tooltip: { mode: 'index', intersect: false },
                    legend: { position: 'top' },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        callback: (value) => (typeof value === 'number' ? value.toLocaleString() : value),
                      },
                    },
                  },
                }}
              />
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}

export default Compare;
