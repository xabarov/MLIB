import { Outlet } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { useNavigationStore } from '../../store/navigationStore'
import { Sidebar } from './Sidebar'

export function AppShell() {
  const toggleMobileNav = useNavigationStore((s) => s.toggleMobileNav)
  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-panel bg-paper/92 px-4 backdrop-blur md:hidden">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
            SHAD Interactive
          </p>
          <p className="text-sm font-semibold text-ink">Миссия</p>
        </div>
        <button
          type="button"
          onClick={toggleMobileNav}
          className="rounded-md border border-ink/10 bg-bg p-2 text-ink shadow-sm"
          aria-label="Открыть навигацию"
          data-testid="mobile-nav-open"
        >
          <Menu className="size-5" />
        </button>
      </header>
      <Sidebar />
      <main className="flex min-h-0 min-w-0 flex-1 flex-col">
        <Outlet />
      </main>
    </div>
  )
}
