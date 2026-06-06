import hintGestureUrl from './mebi-hint-gesture.png'
import hintUrl from './mebi-hint.png'
import idleUrl from './mebi-idle.png'
import successUrl from './mebi-success.png'
import thinkingFocusedUrl from './mebi-thinking-focused.png'
import thinkingUrl from './mebi-thinking.png'
import warningUrl from './mebi-warning.png'

export const mascotImages = {
  idle: idleUrl,
  hint: hintUrl,
  success: successUrl,
  warning: warningUrl,
  thinking: thinkingUrl,
  hintGesture: hintGestureUrl,
  thinkingFocused: thinkingFocusedUrl,
} as const

export type MascotImageKey = keyof typeof mascotImages
