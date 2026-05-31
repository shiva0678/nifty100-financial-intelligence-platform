import { useEffect, useState } from 'react';
import Button from './ui/Button';

const STORAGE_KEY = 'nifty-dark-mode';

function DarkModeToggle() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    const initial = saved
      ? saved === 'true'
      : window.matchMedia('(prefers-color-scheme: dark)').matches;

    setIsDarkMode(initial);
    document.documentElement.classList.toggle('dark', initial);
  }, []);

  const toggleMode = () => {
    const next = !isDarkMode;
    setIsDarkMode(next);
    window.localStorage.setItem(STORAGE_KEY, String(next));
    document.documentElement.classList.toggle('dark', next);
  };

  return (
    <Button variant="ghost" type="button" onClick={toggleMode}>
      {isDarkMode ? 'Light mode' : 'Dark mode'}
    </Button>
  );
}

export default DarkModeToggle;
