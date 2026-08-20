import type { DatasetRow, ThresholdModel } from '../../dataTypes'

type DecisionPlaneProps = {
  rows: DatasetRow[]
  model: ThresholdModel
  selectedRowId?: string
  onModelChange: (model: ThresholdModel) => void
  onRowSelect?: (rowId: string) => void
  xFeatureId?: string
  yFeatureId?: string
}

const view = { min: 8, max: 90 }

function scale(value: number, size: number): number {
  return ((value - view.min) / (view.max - view.min)) * size
}

function clampThreshold(value: number): number {
  return Math.max(10, Math.min(88, Math.round(value)))
}

function numberValue(row: DatasetRow, featureId: string): number {
  const value = row.values[featureId]
  return typeof value === 'number' ? value : 0
}

function pointClass(row: DatasetRow, selected: boolean): string {
  const error = row.flags?.includes('misclassified')
  if (selected) return 'stroke-ink stroke-[3]'
  if (error) return 'stroke-danger stroke-[3]'
  if (row.split === 'test') return 'stroke-energy stroke-[2]'
  return 'stroke-bg stroke-[1.5]'
}

export function DecisionPlane({
  rows,
  model,
  selectedRowId,
  onModelChange,
  onRowSelect,
  xFeatureId = 'signal',
  yFeatureId = 'noise',
}: DecisionPlaneProps) {
  const width = 620
  const height = 360
  const thresholdX = scale(model.threshold, width)

  const updateFromClientX = (clientX: number, rect: DOMRect) => {
    const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
    const threshold = clampThreshold(view.min + ratio * (view.max - view.min))
    onModelChange({ ...model, threshold })
  }

  return (
    <div className="space-y-3" data-testid="decision-plane">
      <div className="relative overflow-hidden rounded-md border border-ink/10 bg-[linear-gradient(180deg,#fffdf7,#f5f1e8)]">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-auto w-full touch-none"
          role="img"
          aria-label="Decision boundary playground"
          data-testid="decision-plane-svg"
          onPointerDown={(event) => {
            const rect = event.currentTarget.getBoundingClientRect()
            updateFromClientX(event.clientX, rect)
            event.currentTarget.setPointerCapture(event.pointerId)
          }}
          onPointerMove={(event) => {
            if (event.buttons !== 1) return
            updateFromClientX(event.clientX, event.currentTarget.getBoundingClientRect())
          }}
        >
          <defs>
            <pattern id="ml-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(20,20,19,0.08)" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width={width} height={height} fill="url(#ml-grid)" />
          <rect x={thresholdX} y="0" width={width - thresholdX} height={height} fill="rgba(89,143,113,0.10)" />
          <rect x="0" y="0" width={thresholdX} height={height} fill="rgba(207,93,63,0.06)" />
          <line
            x1={thresholdX}
            x2={thresholdX}
            y1="18"
            y2={height - 18}
            stroke="rgb(221,112,78)"
            strokeWidth="5"
            strokeLinecap="round"
          />
          <circle cx={thresholdX} cy="34" r="12" fill="rgb(221,112,78)" />
          <text x={thresholdX + 14} y="39" className="fill-ink text-[13px] font-semibold">
            threshold {model.threshold}
          </text>

          {rows.map((row) => {
            const x = scale(numberValue(row, xFeatureId), width)
            const y = height - scale(numberValue(row, yFeatureId), height)
            const selected = row.id === selectedRowId
            const fill = row.label === 1 ? 'rgb(89,143,113)' : 'rgb(77,134,168)'
            return (
              <g
                key={row.id}
                role="button"
                tabIndex={0}
                aria-label={`select ${row.id}`}
                onClick={() => onRowSelect?.(row.id)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') onRowSelect?.(row.id)
                }}
              >
                <circle
                  cx={x}
                  cy={y}
                  r={selected ? 11 : row.split === 'test' ? 8 : 7}
                  fill={fill}
                  className={`${pointClass(row, selected)} cursor-pointer transition`}
                  data-testid={`decision-point-${row.id}`}
                />
                {row.flags?.includes('misclassified') && (
                  <line
                    x1={x - 9}
                    x2={x + 9}
                    y1={y - 9}
                    y2={y + 9}
                    stroke="rgb(185,63,63)"
                    strokeWidth="2"
                  />
                )}
              </g>
            )
          })}
        </svg>
      </div>

      <label className="grid grid-cols-[80px_1fr_52px] items-center gap-2 text-sm text-ink">
        <span className="font-semibold">threshold</span>
        <input
          type="range"
          min={10}
          max={88}
          step={1}
          value={model.threshold}
          onChange={(event) => onModelChange({ ...model, threshold: Number(event.target.value) })}
          className="accent-orange"
          data-testid="ml-threshold-range"
        />
        <input
          type="number"
          min={10}
          max={88}
          value={model.threshold}
          onChange={(event) =>
            onModelChange({ ...model, threshold: clampThreshold(Number(event.target.value)) })
          }
          className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums"
          data-testid="ml-threshold-input"
        />
      </label>
    </div>
  )
}
