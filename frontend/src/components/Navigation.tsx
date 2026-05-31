import { NavLink } from 'react-router-dom';
import DarkModeToggle from './DarkModeToggle';

const navItems = [
  { name: 'Home', path: '/' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Companies', path: '/companies' },
  { name: 'Compare', path: '/compare' },
];

function Navigation() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/95 backdrop-blur-xl">
      <div className="mx-auto flex flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-6">
          <div>
            <NavLink to="/" className="text-xl font-semibold tracking-tight text-white">
              Nifty 100 Finance
            </NavLink>
            <p className="text-sm text-slate-400">Financial data, comparisons, and company insights.</p>
          </div>
          <nav className="flex flex-wrap items-center gap-2 text-sm font-medium text-slate-300">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `rounded-full px-4 py-2 transition ${
                    isActive ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/20' : 'hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="flex items-center justify-end gap-2">
          <DarkModeToggle />
        </div>
      </div>
    </header>
  );
}

export default Navigation;
