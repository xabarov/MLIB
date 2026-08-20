import type { MascotState } from './missionTypes'

export type MissionRuntimeFeedback = {
  mascotState: MascotState
  mascotMessage: string
}

export function chooseMascotState({
  success,
  warning,
  hint,
  thinking,
}: {
  success?: boolean
  warning?: boolean
  hint?: boolean
  thinking?: boolean
}): MascotState {
  if (success) return 'success'
  if (warning) return 'warning'
  if (hint) return 'hint'
  if (thinking) return 'thinking'
  return 'idle'
}

export function missionMessage(
  state: MascotState,
  messages: Record<MascotState, string>,
): string {
  return messages[state]
}
