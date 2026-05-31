import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

function Home() {
  return (
    <section className="space-y-10 pb-12">
      <Card className="rounded-[2rem] border-slate-800 bg-slate-900/90 p-8 shadow-xl shadow-slate-950/20 sm:p-12">
        <div className="max-w-3xl space-y-6">
          <p className="inline-flex rounded-full bg-violet-500/10 px-4 py-1 text-sm font-semibold uppercase tracking-[0.24em] text-violet-200">
            Nifty 100 Dashboard
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Explore Nifty 100 companies with charts, metrics, and smart comparisons.
          </h1>
          <p className="text-lg leading-8 text-slate-300">
            Browse company financials, dive into per-year performance, and compare two Nifty 100 names side by side with interactive visuals.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Link to="/companies">
              <Button>Explore companies</Button>
            </Link>
            <Link to="/compare">
              <Button variant="ghost">Compare companies</Button>
            </Link>
          </div>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        {[
          {
            title: 'Company overview',
            description: 'Quickly access the full profile, financial statements, and latest health score for each Nifty 100 company.',
          },
          {
            title: 'Interactive charts',
            description: 'Visualize revenue, profit, and score trends with beautiful Chart.js graphs.',
          },
          {
            title: 'Side-by-side comparison',
            description: 'Compare up to two companies using the most relevant financial metrics in a clear layout.',
          },
        ].map((item) => (
          <article key={item.title} className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/10">
            <h2 className="text-xl font-semibold text-white">{item.title}</h2>
            <p className="mt-3 text-slate-400">{item.description}</p>
          </article>
        ))}
      </div>

      <Card className="rounded-3xl border-slate-800 bg-slate-900/80 p-8 shadow-xl shadow-slate-950/20">
        <h2 className="text-2xl font-semibold text-white">How it works</h2>
        <ul className="mt-6 space-y-4 text-slate-300">
          <li>
            <strong className="text-white">Browse the Companies page</strong> to see all companies with latest net profit and health score.
          </li>
          <li>
            <strong className="text-white">Open a company detail</strong> for revenue and profit history, cash flow, and score trends.
          </li>
          <li>
            <strong className="text-white">Compare two companies</strong> to surface the strongest financial performers across key metrics.
          </li>
        </ul>
      </Card>
    </section>
  );
}

export default Home;
