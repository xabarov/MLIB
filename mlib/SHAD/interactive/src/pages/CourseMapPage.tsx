import { Compass, KeyRound, Route } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { mascotImages } from '../assets/game/mascot'
import { CoursePath } from '../game/components/CoursePath'
import { MissionCard } from '../game/components/MissionCard'
import { courseMapNodes, missionCompletionRatio, recommendedMissionId } from '../game/courseMap'
import { useProgressStore } from '../store/progressStore'

type CourseFilter = 'all' | 'algebra' | 'algorithms' | 'data-analysis' | 'review'

const courseFilters: { id: CourseFilter; label: string }[] = [
  { id: 'all', label: 'Все' },
  { id: 'algebra', label: 'Алгебра' },
  { id: 'algorithms', label: 'Алгоритмы' },
  { id: 'data-analysis', label: 'Data' },
  { id: 'review', label: 'Повторить' },
]

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
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-5 sm:px-6 lg:px-8">
        <section className="grid gap-4 rounded-md border border-ink/10 bg-panel/35 p-4 shadow-[0_18px_44px_rgba(20,20,19,0.07)] lg:grid-cols-[1fr_280px]">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
              Карта курса
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-normal text-ink">
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
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-orange/25 bg-highlight px-4 py-3">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-orange">
                Рекомендуемая миссия
              </p>
              <p className="text-sm text-ink/72">
                Сейчас лучше открыть: <span className="font-semibold text-ink">{recommendedNode.mission.title}</span>
              </p>
            </div>
            <Link
              to={recommendedNode.mission.route}
              className="inline-flex items-center gap-2 rounded-md border border-orange/30 bg-orange px-3 py-2 text-sm font-semibold text-bg"
              data-testid="course-next-mission"
            >
              <Compass className="size-4" />
              Перейти
            </Link>
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3" data-testid="course-map">
          {visibleNodes.map((node) => {
            const progress = missionCompletionRatio(completedLevels[node.mission.id], node.mission)
            return (
              <MissionCard
                key={node.id}
                node={node}
                completed={progress.completedCount}
                total={progress.totalCount}
                keys={keysByMission[node.mission.id] ?? 0}
                recommended={node.mission.id === recommendedId}
              />
            )
          })}
        </section>

        <div className="flex items-center gap-2 text-xs text-ink/52">
          <Route className="size-4" />
          <span>Маршрут будет расширяться графами, алгоритмами и data playground.</span>
          <KeyRound className="ml-auto hidden size-4 sm:block" />
        </div>
      </div>
    </div>
  )
}
