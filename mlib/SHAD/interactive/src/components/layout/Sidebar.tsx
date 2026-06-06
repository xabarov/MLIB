import { ChevronDown, ChevronRight, FlaskConical, PanelLeftClose, PanelLeft, X } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useNavigationStore } from '../../store/navigationStore'
import { navSections } from '../../visualizations/registry'

export function Sidebar() {
  const collapsed = useNavigationStore((s) => s.sidebarCollapsed)
  const mobileNavOpen = useNavigationStore((s) => s.mobileNavOpen)
  const expandedSections = useNavigationStore((s) => s.expandedSections)
  const expandedTopics = useNavigationStore((s) => s.expandedTopics)
  const toggleSidebar = useNavigationStore((s) => s.toggleSidebar)
  const closeMobileNav = useNavigationStore((s) => s.closeMobileNav)
  const toggleSection = useNavigationStore((s) => s.toggleSection)
  const toggleTopic = useNavigationStore((s) => s.toggleTopic)

  if (collapsed) {
    return (
      <aside className="hidden shrink-0 items-center border-panel bg-panel/30 md:flex md:h-auto md:w-12 md:flex-col md:border-r md:px-0 md:py-3">
        <button
          type="button"
          onClick={toggleSidebar}
          className="rounded p-2 text-ink/70 hover:bg-panel"
          title="Развернуть панель"
        >
          <PanelLeft className="size-5" />
        </button>
      </aside>
    )
  }

  return (
    <aside
      className={`${
        mobileNavOpen ? 'fixed inset-0 z-50 flex' : 'hidden'
      } w-full shrink-0 flex-col border-panel bg-bg/95 backdrop-blur md:static md:z-auto md:flex md:max-h-none md:w-72 md:border-r md:bg-panel/30 md:backdrop-blur-none`}
      data-testid="sidebar"
    >
      <div className="flex items-center justify-between border-b border-panel px-4 py-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink/50">SHAD</p>
          <h1 className="text-sm font-semibold text-ink">Миссии</h1>
        </div>
        <button
          type="button"
          onClick={toggleSidebar}
          className="hidden rounded p-1.5 text-ink/70 hover:bg-panel md:inline-flex"
          title="Свернуть панель"
        >
          <PanelLeftClose className="size-4" />
        </button>
        <button
          type="button"
          onClick={closeMobileNav}
          className="rounded p-1.5 text-ink/70 hover:bg-panel md:hidden"
          aria-label="Закрыть навигацию"
        >
          <X className="size-5" />
        </button>
      </div>

      <nav className="min-h-0 flex-1 overflow-y-auto p-2">
        {navSections.map((section) => {
          const sectionOpen = expandedSections[section.id] ?? true
          return (
            <div key={section.id} className="mb-2">
              <button
                type="button"
                onClick={() => toggleSection(section.id)}
                className="flex w-full items-center gap-1 rounded px-2 py-1.5 text-left text-sm font-semibold text-ink hover:bg-panel/80"
              >
                {sectionOpen ? (
                  <ChevronDown className="size-4 shrink-0" />
                ) : (
                  <ChevronRight className="size-4 shrink-0" />
                )}
                {section.title}
              </button>

              {sectionOpen &&
                section.topics.map((topic) => {
                  const topicOpen = expandedTopics[topic.id] ?? true
                  return (
                    <div key={topic.id} className="ml-3 mt-1">
                      <button
                        type="button"
                        onClick={() => toggleTopic(topic.id)}
                        className="flex w-full items-center gap-1 rounded px-2 py-1 text-left text-xs font-medium text-ink/80 hover:bg-panel/80"
                      >
                        {topicOpen ? (
                          <ChevronDown className="size-3.5 shrink-0" />
                        ) : (
                          <ChevronRight className="size-3.5 shrink-0" />
                        )}
                        {topic.title}
                      </button>

                      {topicOpen && (
                        <ul className="ml-4 mt-0.5 space-y-0.5 border-l border-gray/50 pl-2">
                          {topic.visualizations.map((viz) => (
                            <li key={viz.id}>
                              {viz.status !== 'planned' ? (
                                <NavLink
                                  to={viz.path}
                                  onClick={closeMobileNav}
                                  className={({ isActive }) =>
                                    `flex items-start gap-1.5 rounded px-2 py-1.5 text-xs leading-snug transition-colors ${
                                      isActive
                                        ? 'bg-orange/15 font-medium text-ink'
                                        : 'text-ink/75 hover:bg-panel/60 hover:text-ink'
                                    }`
                                  }
                                >
                                  {viz.kind === 'mission' && (
                                    <FlaskConical className="mt-0.5 size-3.5 shrink-0 text-orange" />
                                  )}
                                  <span className="min-w-0">
                                    <span className="block">{viz.title}</span>
                                    {viz.status === 'prototype' && (
                                      <span className="text-[10px] uppercase tracking-wide text-target">
                                        прототип
                                      </span>
                                    )}
                                  </span>
                                </NavLink>
                              ) : (
                                <span
                                  className="block cursor-not-allowed rounded px-2 py-1.5 text-xs leading-snug text-ink/40"
                                  title="Скоро"
                                >
                                  {viz.title}
                                  <span className="ml-1 text-[10px] uppercase">скоро</span>
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )
                })}
            </div>
          )
        })}
      </nav>
    </aside>
  )
}
