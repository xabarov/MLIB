import katex from 'katex'
import { useMemo } from 'react'

type MathBlockProps = {
  math: string
  display?: boolean
  className?: string
}

export function MathBlock({ math, display = true, className = '' }: MathBlockProps) {
  const html = useMemo(
    () => katex.renderToString(math, { throwOnError: false, displayMode: display }),
    [math, display],
  )

  return (
    <span
      className={`${display ? 'block overflow-x-auto py-1' : ''} ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
