import { mascotImages } from '../../assets/game/mascot'
import type { MascotState } from '../missionTypes'

type MascotCoachProps = {
  state: MascotState
  message: string
}

const imageByState: Record<MascotState, string> = {
  idle: mascotImages.idle,
  hint: mascotImages.hintGesture,
  success: mascotImages.success,
  warning: mascotImages.warning,
  thinking: mascotImages.thinkingFocused,
}

export function MascotCoach({ state, message }: MascotCoachProps) {
  return (
    <div className="flex min-w-0 items-end gap-3">
      <img
        src={imageByState[state]}
        alt="Меби"
        className="h-auto w-[78px] shrink-0 drop-shadow-[0_12px_18px_rgba(20,20,19,0.16)] sm:w-[96px] xl:w-[118px]"
      />
      <p className="min-w-0 rounded-md border border-ink/10 bg-bg/80 px-3 py-2 text-sm leading-snug text-ink shadow-sm">
        {message}
      </p>
    </div>
  )
}
