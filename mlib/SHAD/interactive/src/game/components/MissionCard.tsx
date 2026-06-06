import { ArrowRight, BookOpen, CheckCircle2, KeyRound, Play } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { CourseMapNode } from '../courseMap'

type MissionCardProps = {
  node: CourseMapNode
  completed: number
  total: number
  keys: number
  recommended: boolean
}

export function MissionCard({ node, completed, total, keys, recommended }: MissionCardProps) {
  const complete = completed >= total
  const progressPct = total === 0 ? 0 : Math.round((completed / total) * 100)

  return (
    <article
      className={`relative flex min-h-56 flex-col justify-between rounded-md border bg-paper p-4 shadow-[0_18px_42px_rgba(20,20,19,0.08)] transition ${
        recommended
          ? 'border-orange/55 ring-2 ring-orange/16'
          : complete
            ? 'border-success/35'
            : 'border-ink/10'
      }`}
      data-testid={`course-card-${node.mission.id}`}
    >
      <div>
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
              {node.label}
            </p>
            <h2 className="mt-1 text-lg font-semibold leading-tight text-ink">{node.mission.title}</h2>
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

        <div className="mt-4 h-2 overflow-hidden rounded-full bg-panel">
          <div
            className={`h-full rounded-full ${complete ? 'bg-success' : 'bg-orange'}`}
            style={{ width: `${progressPct}%` }}
          />
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <span className="inline-flex items-center gap-1 rounded border border-ink/10 bg-bg px-2 py-1 text-ink/70">
            <CheckCircle2 className="size-3.5" />
            {completed}/{total} уровней
          </span>
          <span className="inline-flex items-center gap-1 rounded border border-ink/10 bg-bg px-2 py-1 text-ink/70">
            <KeyRound className="size-3.5" />
            {keys} ключей
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
