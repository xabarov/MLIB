import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Dices,
  KeyRound,
  ListOrdered,
  Network,
  Play,
  Route,
  Shapes,
  Target,
  Workflow,
  type LucideIcon,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import type { CourseMapNode } from '../courseMap'

const STATION_ACCENT: Record<string, string> = {
  algebra: 'var(--color-target)',
  combinatorics: 'var(--color-green)',
  algorithms: 'var(--color-purple)',
  'data-analysis': 'var(--color-energy)',
  probability: 'var(--color-blue)',
  calculus: 'var(--color-success)',
}

const MECHANIC_ICON: Record<string, LucideIcon> = {
  'geometry-lab': Shapes,
  'state-machine': Workflow,
  'structure-builder': Network,
  sampler: Dices,
  'model-arena': Target,
  'code-trace': ListOrdered,
}

type MissionCardProps = {
  node: CourseMapNode
  completed: number
  total: number
  keys: number
  recommended: boolean
}

export function MissionCard({ node, completed, total, keys, recommended }: MissionCardProps) {
  const complete = completed >= total
  const accent = STATION_ACCENT[node.station] ?? 'var(--color-orange)'
  const MechIcon = MECHANIC_ICON[node.mission.mechanic] ?? Shapes
  const progressPct = total === 0 ? 0 : Math.round((completed / total) * 100)
  const ringR = 19
  const ringC = 2 * Math.PI * ringR
  const ringColor = complete ? 'var(--color-success)' : accent

  return (
    <article
      className={`relative flex h-full w-full min-h-56 flex-col justify-between rounded-md border border-l-[3px] bg-paper p-4 shadow-[0_18px_42px_rgba(20,20,19,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_22px_50px_rgba(20,20,19,0.12)] ${
        recommended
          ? 'border-orange/55 ring-2 ring-orange/16'
          : complete
            ? 'border-success/35'
            : 'border-ink/10'
      }`}
      style={{ borderLeftColor: accent }}
      data-testid={`course-card-${node.mission.id}`}
    >
      <div>
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-start gap-2.5">
            <span
              className="relative mt-0.5 grid size-11 shrink-0 place-items-center"
              aria-hidden
              title={`${progressPct}% пройдено`}
            >
              <svg className="absolute inset-0 size-11 -rotate-90" viewBox="0 0 44 44">
                <circle cx="22" cy="22" r={ringR} fill="none" stroke="var(--color-panel)" strokeWidth="3" />
                <circle
                  cx="22"
                  cy="22"
                  r={ringR}
                  fill="none"
                  stroke={ringColor}
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeDasharray={ringC}
                  strokeDashoffset={ringC * (1 - progressPct / 100)}
                />
              </svg>
              <span
                className="grid size-8 place-items-center rounded-full"
                style={{ color: accent, background: `color-mix(in srgb, ${accent} 12%, transparent)` }}
              >
                <MechIcon className="size-4" />
              </span>
            </span>
            <div className="min-w-0">
              <p className="text-[10px] font-semibold uppercase tracking-[0.12em]" style={{ color: accent }}>
                {node.label}
              </p>
              <h2 className="mt-1 font-display text-xl font-semibold leading-tight tracking-tight text-ink">
                {node.mission.title}
              </h2>
            </div>
          </div>
          <span
            className={`inline-flex shrink-0 items-center rounded border px-2 py-1 text-[10px] font-semibold uppercase tracking-wide ${
              complete
                ? 'border-success/35 bg-success/12 text-success'
                : recommended
                  ? 'border-orange/35 bg-orange/12 text-orange'
                  : 'border-ink/10 bg-bg text-ink/55'
            }`}
          >
            {complete ? 'готово' : recommended ? 'следующий' : node.station}
          </span>
        </div>

        <p className="text-sm leading-relaxed text-ink/68">{node.shortIdea}</p>

        <div className="mt-3 space-y-2 text-xs text-ink/62">
          <p className="rounded border border-ink/10 bg-bg px-2 py-1">
            Навык: <span className="font-semibold text-ink">{node.curriculum.skillIds[0]}</span>
          </p>
          <p className="rounded border border-ink/10 bg-bg px-2 py-1">
            Готовность:{' '}
            <span className="font-semibold text-ink">{node.curriculum.readinessLabel}</span>
          </p>
          {node.curriculum.unlocks.length > 0 && (
            <p className="inline-flex w-full items-center gap-1 rounded border border-ink/10 bg-bg px-2 py-1">
              <Route className="size-3.5 shrink-0" />
              <span className="truncate">Открывает: {node.curriculum.unlocks.join(', ')}</span>
            </p>
          )}
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
          <span className="inline-flex items-center gap-1 rounded border border-ink/10 bg-bg px-2 py-1 text-ink/70">
            <CheckCircle2 className="size-3.5" />
            {completed}/{total} уровней
          </span>
          <span className="inline-flex items-center gap-1 rounded border border-ink/10 bg-bg px-2 py-1 text-ink/70">
            <KeyRound className="size-3.5" />
            {keys} ключей
          </span>
          <span className="col-span-2 rounded border border-ink/10 bg-bg px-2 py-1 text-ink/70">
            {node.curriculum.coverageStatus}
          </span>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <Link
          to={node.mission.route}
          className="inline-flex items-center gap-1.5 rounded-md border border-orange/30 bg-orange px-3 py-2 text-sm font-semibold text-bg shadow-sm transition hover:bg-orange/90"
          data-testid={`course-start-${node.mission.id}`}
        >
          <Play className="size-4" />
          Запустить
        </Link>
        {node.mission.lessonPath && (
          <span className="inline-flex min-w-0 items-center gap-1 rounded-md border border-ink/10 bg-bg px-2 py-2 text-xs text-ink/58">
            <BookOpen className="size-3.5 shrink-0" />
            <span className="truncate">{node.mission.lessonPath}</span>
          </span>
        )}
      </div>

      {recommended && !complete && (
        <div className="absolute -right-2 -top-2 inline-flex size-8 items-center justify-center rounded-full border border-orange/30 bg-highlight text-orange shadow-sm">
          <ArrowRight className="size-4" />
        </div>
      )}
    </article>
  )
}
