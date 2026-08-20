import hintGestureUrl from './mebi-hint-gesture.webp'
import hintUrl from './mebi-hint.webp'
import idleUrl from './mebi-idle.webp'
import successUrl from './mebi-success.webp'
import thinkingFocusedUrl from './mebi-thinking-focused.webp'
import thinkingUrl from './mebi-thinking.webp'
import warningUrl from './mebi-warning.webp'

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
