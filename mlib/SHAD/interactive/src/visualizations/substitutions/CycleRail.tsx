import { cycleEdgeStates, type Permutation } from './substitutionWorkshopModel'

type CycleRailProps = {
  permutation: Permutation
  target?: Permutation
}

function point(index: number, size: number) {
  const angle = -Math.PI / 2 + (index / size) * Math.PI * 2
  return {
    x: 50 + Math.cos(angle) * 36,
    y: 50 + Math.sin(angle) * 34,
  }
}

export function CycleRail({ permutation, target }: CycleRailProps) {
  const edges = cycleEdgeStates(permutation, target)
  const size = permutation.length

  return (
    <div className="rounded-md border border-ink/10 bg-paper/82 p-3" data-testid="cycle-rail">
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          cycle rail
        </p>
        <span className="text-xs font-semibold text-ink/52">
          {edges.filter((edge) => edge.correct).length}/{edges.length} arrows
        </span>
      </div>
      <svg viewBox="0 0 100 100" className="h-56 w-full" role="img" aria-label="Маршрут перестановки">
        <defs>
          <marker id="cycle-arrow-ok" markerHeight="5" markerWidth="5" orient="auto" refX="4" refY="2.5">
            <path d="M0,0 L5,2.5 L0,5 Z" fill="#598f71" />
          </marker>
          <marker id="cycle-arrow-bad" markerHeight="5" markerWidth="5" orient="auto" refX="4" refY="2.5">
            <path d="M0,0 L5,2.5 L0,5 Z" fill="#d66545" />
          </marker>
          <marker id="cycle-arrow-ghost" markerHeight="5" markerWidth="5" orient="auto" refX="4" refY="2.5">
            <path d="M0,0 L5,2.5 L0,5 Z" fill="#1f1f1f" opacity="0.35" />
          </marker>
        </defs>

        {target?.map((to, index) => {
          const fromPoint = point(index, size)
          const toPoint = point(to - 1, size)
          return (
            <line
              key={`target-${index}`}
              x1={fromPoint.x}
              y1={fromPoint.y}
              x2={toPoint.x}
              y2={toPoint.y}
              stroke="#1f1f1f"
              strokeDasharray="2 3"
              strokeOpacity="0.22"
              strokeWidth="1.2"
              markerEnd="url(#cycle-arrow-ghost)"
            />
          )
        })}

        {edges.map((edge) => {
          const fromPoint = point(edge.from - 1, size)
          const toPoint = point(edge.to - 1, size)
          return (
            <line
              key={`edge-${edge.from}`}
              x1={fromPoint.x}
              y1={fromPoint.y}
              x2={toPoint.x}
              y2={toPoint.y}
              stroke={edge.correct ? '#598f71' : '#d66545'}
              strokeOpacity="0.88"
              strokeWidth={edge.correct ? 2.4 : 3}
              markerEnd={edge.correct ? 'url(#cycle-arrow-ok)' : 'url(#cycle-arrow-bad)'}
            />
          )
        })}

        {permutation.map((value, index) => {
          const currentPoint = point(index, size)
          const correct = target ? target[index] === value : true
          return (
            <g key={`node-${index}`}>
              <circle
                cx={currentPoint.x}
                cy={currentPoint.y}
                r="6.5"
                fill={correct ? '#ecf5ee' : '#fff1ec'}
                stroke={correct ? '#598f71' : '#d66545'}
                strokeWidth="1.8"
              />
              <text
                x={currentPoint.x}
                y={currentPoint.y + 1.5}
                textAnchor="middle"
                className="fill-ink text-[7px] font-semibold"
              >
                {index + 1}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
