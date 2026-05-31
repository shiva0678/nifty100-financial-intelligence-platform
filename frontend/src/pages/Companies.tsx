import { FormEvent, useEffect, useState } from 'react';
import { fetchCompanies, searchCompanies } from '../api';
import type { CompanySummary } from '../types';
import CompanyCard from '../components/CompanyCard';
import LoadingSpinner from '../components/LoadingSpinner';
import SearchBar from '../components/SearchBar';

function Companies() {
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeSearch, setActiveSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadCompanies = (query = '', page = 1) => {
    setIsLoading(true);
    setErrorMessage(null);

    const request = query ? searchCompanies(query, page, 50) : fetchCompanies(page, 50);

    request
      .then((result) => {
        setCompanies(result.results);
      })
      .catch((error) => {
        setErrorMessage(error.message);
        setCompanies([]);
      })
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadCompanies();
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalized = searchTerm.trim();
    setActiveSearch(normalized);
    loadCompanies(normalized);
  };

  const handleClear = () => {
    setSearchTerm('');
    setActiveSearch('');
    loadCompanies();
  };

  return (
    <section className="space-y-8">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/20 sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-white">All Companies</h1>
            <p className="mt-2 text-slate-400">
              Browse the Nifty 100 companies and inspect the latest financial performance at a glance.
            </p>
          </div>
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            onSubmit={handleSubmit}
            onClear={handleClear}
            placeholder="Search ticker or company name"
            loading={isLoading}
          />
        </div>
        {activeSearch ? (
          <p className="mt-4 text-sm text-slate-400">
            Showing results for <span className="font-semibold text-white">"{activeSearch}"</span>.
          </p>
        ) : null}
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : errorMessage ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-200">
          <strong className="block text-lg">Unable to load companies</strong>
          <p className="mt-2 text-sm text-slate-300">{errorMessage}</p>
        </div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-2">
          {companies.length > 0 ? (
            companies.map((company) => <CompanyCard key={company.company_id} company={company} />)
          ) : (
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-8 text-slate-300">
              {activeSearch
                ? 'No companies matched your search. Try another ticker or company name.'
                : 'No companies available at the moment. Please try again later.'}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default Companies;
