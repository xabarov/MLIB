import { Compass, KeyRound, Route } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { mascotImages } from '../assets/game/mascot'
import { CoursePath } from '../game/components/CoursePath'
import { MissionCard } from '../game/components/MissionCard'
import { courseMapNodes, missionCompletionRatio, recommendedMissionId } from '../game/courseMap'
import { useProgressStore } from '../store/progressStore'

type CourseFilter =
  | 'all'
  | 'algebra'
  | 'algorithms'
  | 'data-analysis'
  | 'probability'
  | 'calculus'
  | 'review'

const courseFilters: { id: CourseFilter; label: string }[] = [
  { id: 'all', label: 'Все' },
  { id: 'algebra', label: 'Алгебра' },
  { id: 'algorithms', label: 'Алгоритмы' },
  { id: 'data-analysis', label: 'Data' },
  { id: 'probability', label: 'Вероятность' },
  { id: 'calculus', label: 'Анализ' },
  { id: 'review', label: 'Повторить' },
]

const SECTION_ORDER = [
  'algebra',
  'combinatorics',
  'algorithms',
  'data-analysis',
  'probability',
  'calculus',
] as const

const SECTION_META: Record<string, { label: string; accent: string }> = {
  algebra: { label: 'Линейная алгебра', accent: 'var(--color-target)' },
  combinatorics: { label: 'Комбинаторика и графы', accent: 'var(--color-green)' },
  algorithms: { label: 'Алгоритмы и структуры', accent: 'var(--color-purple)' },
  'data-analysis': { label: 'Анализ данных', accent: 'var(--color-energy)' },
  probability: { label: 'Вероятность', accent: 'var(--color-blue)' },
  calculus: { label: 'Математический анализ', accent: 'var(--color-success)' },
}

export function CourseMapPage() {
  const [filter, setFilter] = useState<CourseFilter>('all')
  const completedLevels = useProgressStore((s) => s.completedLevels)
  const keysByMission = useProgressStore((s) => s.keysByMission)
  const keys = useProgressStore((s) => s.keys)
  const recommendedId = recommendedMissionId(completedLevels)
  const recommendedNode = courseMapNodes.find((node) => node.mission.id === recommendedId)
  const completedMissions = courseMapNodes.filter(
    (node) => missionCompletionRatio(completedLevels[node.mission.id], node.mission).complete,
  ).length
  const visibleNodes = useMemo(
    () =>
      courseMapNodes.filter((node) => {
        const progress = missionCompletionRatio(completedLevels[node.mission.id], node.mission)
        if (filter === 'all') return true
        if (filter === 'review') return progress.complete || node.curriculum.reviewAfterMissionIds?.length
        return node.curriculum.section === filter
      }),
    [completedLevels, filter],
  )

  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-[linear-gradient(180deg,#fffdf7,#faf9f5)]">
      <div className="relative mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8 draft-grid">
        <section className="grid gap-4 rounded-md border border-ink/10 bg-panel/35 p-4 shadow-[0_18px_44px_rgba(20,20,19,0.07)] lg:grid-cols-[1fr_280px]">
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-orange">
              Карта курса
            </p>
            <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
              Математическая мастерская
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink/68">
              Проходи короткие миссии в порядке маршрута: каждая дает действие,
              инвариант и одну идею, которую стоит вернуть обратно в лекцию.
            </p>
            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              <div className="rounded-md border border-ink/10 bg-paper px-3 py-2">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                  миссии
                </p>
                <p className="mt-1 text-lg font-semibold tabular-nums text-ink">
                  {completedMissions}/{courseMapNodes.length}
                </p>
              </div>
              <div className="rounded-md border border-ink/10 bg-paper px-3 py-2">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                  инвариант-ключи
                </p>
                <p className="mt-1 text-lg font-semibold tabular-nums text-ink">{keys}</p>
              </div>
              <div className="rounded-md border border-orange/25 bg-highlight px-3 py-2">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
                  следующий шаг
                </p>
                <p className="mt-1 truncate text-lg font-semibold text-ink">
                  {recommendedNode?.mission.title ?? 'Маршрут собран'}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-end gap-3 rounded-md border border-ink/10 bg-bg/75 p-3">
            <img
              src={mascotImages.hintGesture}
              alt="Меби"
              className="h-auto w-24 shrink-0 drop-shadow-[0_12px_18px_rgba(20,20,19,0.16)]"
            />
            <div className="min-w-0">
              <p className="text-sm font-semibold text-ink">Меби ведет по инвариантам.</p>
              <p className="mt-1 text-xs leading-relaxed text-ink/62">
                Сначала бери следующую подсвеченную миссию; после успеха карта
                сама покажет новый маршрут.
              </p>
            </div>
          </div>
        </section>

        <CoursePath nodes={courseMapNodes} recommendedMissionId={recommendedId} />

        <div className="flex flex-wrap gap-2" aria-label="Фильтр карты курса">
          {courseFilters.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setFilter(item.id)}
              className={`rounded-md border px-3 py-2 text-sm font-semibold transition ${
                filter === item.id
                  ? 'border-orange/35 bg-orange text-bg'
                  : 'border-ink/10 bg-paper text-ink/70 hover:border-orange/35 hover:text-ink'
              }`}
              data-testid={`course-filter-${item.id}`}
            >
              {item.label}
            </button>
          ))}
        </div>

        {recommendedNode && (
          <div className="relative flex flex-wrap items-center justify-between gap-4 overflow-hidden rounded-lg border border-orange/30 bg-gradient-to-r from-highlight to-paper px-5 py-4 shadow-[0_14px_34px_rgba(217,119,87,0.12)]">
            <div className="min-w-0">
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-orange">
                Рекомендуемая миссия
              </p>
              <p className="mt-1 font-display text-2xl font-semibold tracking-tight text-ink sm:text-[1.7rem]">
                {recommendedNode.mission.title}
              </p>
              <p className="mt-1 max-w-xl text-sm leading-relaxed text-ink/60">
                {recommendedNode.curriculum.takeaway}
              </p>
            </div>
            <Link
              to={recommendedNode.mission.route}
              className="inline-flex shrink-0 items-center gap-2 rounded-md border border-orange/30 bg-orange px-4 py-2.5 text-sm font-semibold text-bg shadow-sm transition hover:brightness-105"
              data-testid="course-next-mission"
            >
              <Compass className="size-4" />
              Перейти
            </Link>
          </div>
        )}

        <div className="space-y-7" data-testid="course-map">
          {SECTION_ORDER.map((station) => {
            const sectionNodes = visibleNodes.filter((node) => node.station === station)
            if (sectionNodes.length === 0) return null
            const meta = SECTION_META[station]
            return (
              <section key={station} className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="size-3 shrink-0 rounded-full" style={{ background: meta.accent }} />
                  <h2 className="font-display text-lg font-semibold tracking-tight text-ink">
                    {meta.label}
                  </h2>
                  <span className="text-xs font-semibold tabular-nums text-ink/40">
                    {sectionNodes.length}
                  </span>
                  <span className="h-px flex-1 bg-ink/10" />
                </div>
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {sectionNodes.map((node, index) => {
                    const progress = missionCompletionRatio(
                      completedLevels[node.mission.id],
                      node.mission,
                    )
                    return (
                      <div
                        key={node.id}
                        className="card-rise flex"
                        style={{ animationDelay: `${Math.min(index, 10) * 30}ms` }}
                      >
                        <MissionCard
                          node={node}
                          completed={progress.completedCount}
                          total={progress.totalCount}
                          keys={keysByMission[node.mission.id] ?? 0}
                          recommended={node.mission.id === recommendedId}
                        />
                      </div>
                    )
                  })}
                </div>
              </section>
            )
          })}
        </div>

        <div className="flex items-center gap-2 text-xs text-ink/52">
          <Route className="size-4" />
          <span>Маршрут будет расширяться графами, алгоритмами и data playground.</span>
          <KeyRound className="ml-auto hidden size-4 sm:block" />
        </div>
      </div>
    </div>
  )
}
