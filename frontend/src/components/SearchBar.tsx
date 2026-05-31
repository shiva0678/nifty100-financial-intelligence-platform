import type { FormEvent } from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onClear: () => void;
  placeholder?: string;
  loading?: boolean;
}

function SearchBar({ value, onChange, onSubmit, onClear, placeholder = 'Search', loading = false }: SearchBarProps) {
  return (
    <form className="flex w-full max-w-xl flex-col gap-3 sm:flex-row sm:items-center" onSubmit={onSubmit}>
      <label htmlFor="company-search" className="sr-only">
        Search companies
      </label>
      <div className="flex flex-1 items-center gap-3 rounded-full border border-slate-800 bg-slate-950 px-4 py-3">
        <input
          id="company-search"
          type="search"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="w-full bg-transparent text-slate-100 outline-none placeholder:text-slate-500"
        />
        {value ? (
          <button
            type="button"
            onClick={onClear}
            className="rounded-full bg-slate-800 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-700"
          >
            Clear
          </button>
        ) : null}
      </div>
      <button
        type="submit"
        disabled={loading}
        className="inline-flex shrink-0 items-center justify-center rounded-full bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? 'Searching…' : 'Search'}
      </button>
    </form>
  );
}

export default SearchBar;
