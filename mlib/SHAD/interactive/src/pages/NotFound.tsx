import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8">
      <p className="text-ink/70">Страница не найдена.</p>
      <Link
        to="/algebra/linear-maps/kernel"
        className="text-sm text-blue underline-offset-2 hover:underline"
      >
        Ядро линейного отображения
      </Link>
    </div>
  )
}
