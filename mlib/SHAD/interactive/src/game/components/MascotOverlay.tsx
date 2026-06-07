import { mascotImages } from '../../assets/game/mascot'
import type { MascotRole, MascotState } from '../missionTypes'

type MascotOverlayProps = {
  role: MascotRole
  state: MascotState
  label: string
  xPercent: number
  yPercent: number
}

const roleLabel: Record<MascotRole, string> = {
  guide: 'подсказка',
  pivot: 'опора',
  frontier: 'frontier',
  'error-marker': 'ошибка',
  'invariant-token': 'инвариант',
  'data-point': 'точка',
  'metric-inspector': 'метрика',
}

const imageByState: Record<MascotState, string> = {
  idle: mascotImages.idle,
  hint: mascotImages.hintGesture,
  success: mascotImages.success,
  warning: mascotImages.warning,
  thinking: mascotImages.thinkingFocused,
}

export function MascotOverlay({
  role,
  state,
  label,
  xPercent,
  yPercent,
}: MascotOverlayProps) {
  return (
    <div
      className="pointer-events-none absolute z-20 hidden -translate-x-1/2 -translate-y-full items-end gap-1 sm:flex"
      style={{ left: `${xPercent}%`, top: `${yPercent}%` }}
      data-testid={`mascot-overlay-${role}`}
    >
      <img
        src={imageByState[state]}
        alt=""
        className="h-auto w-12 drop-shadow-[0_10px_18px_rgba(20,20,19,0.18)]"
      />
      <span className="rounded border border-ink/10 bg-bg/90 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-ink/70 shadow-sm">
        {roleLabel[role]}: {label}
      </span>
    </div>
  )
}
