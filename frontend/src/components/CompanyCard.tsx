import type { CompanySummary } from '../types';
import { Link } from 'react-router-dom';

interface CompanyCardProps {
  company: CompanySummary;
}

function CompanyCard({ company }: CompanyCardProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl shadow-slate-950/20 transition hover:-translate-y-1 hover:border-violet-500 sm:p-6">
      <div className="flex items-start gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-800 text-2xl font-semibold text-violet-400">
          {company.ticker.slice(0, 2)}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-white">{company.company_name}</h3>
          <p className="mt-1 truncate text-sm text-slate-400">{company.ticker}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl bg-slate-950/80 p-4 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Latest Net Profit</p>
          <p className="mt-2 text-base font-semibold text-white">
            {company.latest_net_profit != null ? `₹${company.latest_net_profit.toLocaleString()}` : 'N/A'}
          </p>
        </div>
        <div className="rounded-2xl bg-slate-950/80 p-4 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Health Score</p>
          <p className="mt-2 text-base font-semibold text-white">
            {company.health_score ?? '—'} {company.health_label ? `(${company.health_label})` : ''}
          </p>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <Link
          to={`/company/${company.ticker}`}
          className="inline-flex rounded-full bg-violet-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-400"
        >
          View details
        </Link>
        {company.website ? (
          <a
            href={company.website}
            target="_blank"
            rel="noreferrer"
            className="inline-flex rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-200 transition hover:border-violet-500 hover:text-white"
          >
            Visit site
          </a>
        ) : null}
      </div>
    </div>
  );
}

export default CompanyCard;
