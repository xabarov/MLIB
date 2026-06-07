import type { DatasetColumn, DatasetRow } from '../../dataTypes'

export type DataTableAction = {
  id: string
  label: string
  targetIds?: string[]
}

type DataTableMiniProps = {
  rows: DatasetRow[]
  columns: DatasetColumn[]
  selectedRowId?: string
  onRowSelect?: (rowId: string) => void
  rowActions?: DataTableAction[]
  columnActions?: DataTableAction[]
  onRowAction?: (actionId: string, rowId: string) => void
  onColumnAction?: (actionId: string, columnId: string) => void
  highlightMode?: 'errors' | 'leakage' | 'split'
  maxRowsCollapsed?: number
}

function formatValue(value: number | string | null): string {
  if (value === null) return 'NA'
  if (typeof value === 'number') return Number.isInteger(value) ? String(value) : value.toFixed(2)
  return value
}

function splitClass(split: DatasetRow['split']) {
  return split === 'train'
    ? 'border-target/25 bg-target/10 text-target'
    : 'border-energy/25 bg-energy/10 text-energy'
}

function rowClass(row: DatasetRow, selected: boolean, highlightMode: DataTableMiniProps['highlightMode']) {
  const misclassified = row.flags?.includes('misclassified')
  const leakage = row.flags?.includes('leakage')
  if (selected) return 'border-orange/45 bg-orange/12'
  if (highlightMode === 'errors' && misclassified) return 'border-danger/35 bg-danger/10'
  if (highlightMode === 'leakage' && leakage) return 'border-orange/35 bg-orange/10'
  return 'border-ink/10 bg-bg/72'
}

function actionsForTarget(actions: DataTableAction[], targetId: string) {
  return actions.filter((action) => !action.targetIds || action.targetIds.includes(targetId))
}

export function DataTableMini({
  rows,
  columns,
  selectedRowId,
  onRowSelect,
  rowActions = [],
  columnActions = [],
  onRowAction,
  onColumnAction,
  highlightMode = 'errors',
  maxRowsCollapsed,
}: DataTableMiniProps) {
  const visibleRows = maxRowsCollapsed ? rows.slice(0, maxRowsCollapsed) : rows
  const hiddenCount = Math.max(0, rows.length - visibleRows.length)
  const hasRowActions = rowActions.length > 0
  const hasColumnActions = columnActions.length > 0
  const tableGridStyle = {
    gridTemplateColumns: `64px 58px 58px repeat(${columns.length}, minmax(44px, 1fr))${
      hasRowActions ? ' minmax(98px, 0.7fr)' : ''
    }`,
  }

  return (
    <div className="space-y-2" data-testid="data-table-mini">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          samples
        </p>
        <span className="text-xs font-semibold tabular-nums text-ink/50">
          {rows.length} rows
        </span>
      </div>

      <div className="hidden overflow-hidden rounded-md border border-ink/10 bg-paper/70 sm:block">
        <div
          className="grid border-b border-ink/10 bg-ink/[0.035] px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-ink/45"
          style={tableGridStyle}
        >
          <span>id</span>
          <span>split</span>
          <span>y/pred</span>
          {columns.map((column) => (
            <span key={column.id} className="min-w-0">
              <span className="block truncate">{column.label}</span>
              {hasColumnActions && (
                <span className="mt-1 flex flex-wrap gap-1">
                  {actionsForTarget(columnActions, column.id).map((action) => (
                    <button
                      key={action.id}
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation()
                        onColumnAction?.(action.id, column.id)
                      }}
                      className="rounded border border-ink/10 bg-bg/80 px-1.5 py-0.5 text-[9px] font-semibold text-ink/58 transition hover:border-orange/30 hover:text-ink"
                      data-testid={`data-column-action-${action.id}-${column.id}`}
                    >
                      {action.label}
                    </button>
                  ))}
                </span>
              )}
            </span>
          ))}
          {hasRowActions && <span>action</span>}
        </div>
        <div className="max-h-64 overflow-y-auto">
          {visibleRows.map((row) => {
            const selected = row.id === selectedRowId
            return (
              <button
                key={row.id}
                type="button"
                onClick={() => onRowSelect?.(row.id)}
                className={`grid w-full items-center border-b px-2 py-1.5 text-left text-xs transition last:border-b-0 ${rowClass(
                  row,
                  selected,
                  highlightMode,
                )}`}
                style={tableGridStyle}
                data-testid={`data-row-${row.id}`}
              >
                <span className="font-mono text-ink/62">{row.id}</span>
                <span
                  className={`mr-2 rounded border px-1.5 py-0.5 text-[10px] font-semibold ${splitClass(
                    row.split,
                  )}`}
                >
                  {row.split}
                </span>
                <span className="font-semibold tabular-nums text-ink">
                  {row.label}/{row.prediction ?? '-'}
                </span>
                {columns.map((column) => (
                  <span key={column.id} className="tabular-nums text-ink/70">
                    {formatValue(row.values[column.id])}
                  </span>
                ))}
                {hasRowActions && (
                  <span className="flex flex-wrap gap-1">
                    {actionsForTarget(rowActions, row.id).map((action) => (
                      <span
                        key={action.id}
                        role="button"
                        tabIndex={0}
                        onClick={(event) => {
                          event.stopPropagation()
                          onRowAction?.(action.id, row.id)
                        }}
                        onKeyDown={(event) => {
                          if (event.key !== 'Enter' && event.key !== ' ') return
                          event.preventDefault()
                          event.stopPropagation()
                          onRowAction?.(action.id, row.id)
                        }}
                        className="rounded border border-ink/10 bg-paper/90 px-1.5 py-0.5 text-[10px] font-semibold text-ink/62 transition hover:border-orange/30 hover:text-ink"
                        data-testid={`data-row-action-${action.id}-${row.id}`}
                      >
                        {action.label}
                      </span>
                    ))}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      <div className="grid gap-2 sm:hidden">
        {visibleRows.map((row) => {
          const selected = row.id === selectedRowId
          return (
            <button
              key={row.id}
              type="button"
              onClick={() => onRowSelect?.(row.id)}
              className={`rounded-md border p-2 text-left transition ${rowClass(
                row,
                selected,
                highlightMode,
              )}`}
              data-testid={`data-row-${row.id}`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-xs font-semibold text-ink">{row.id}</span>
                <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold ${splitClass(row.split)}`}>
                  {row.split}
                </span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-1 text-xs text-ink/66">
                <span>
                  y/pred <b className="text-ink">{row.label}/{row.prediction ?? '-'}</b>
                </span>
                {columns.map((column) => (
                  <span key={column.id}>
                    {column.label} <b className="text-ink">{formatValue(row.values[column.id])}</b>
                  </span>
                ))}
              </div>
              {hasRowActions && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {actionsForTarget(rowActions, row.id).map((action) => (
                    <span
                      key={action.id}
                      role="button"
                      tabIndex={0}
                      onClick={(event) => {
                        event.stopPropagation()
                        onRowAction?.(action.id, row.id)
                      }}
                      onKeyDown={(event) => {
                        if (event.key !== 'Enter' && event.key !== ' ') return
                        event.preventDefault()
                        event.stopPropagation()
                        onRowAction?.(action.id, row.id)
                      }}
                      className="rounded border border-ink/10 bg-paper/90 px-2 py-1 text-[10px] font-semibold text-ink/62"
                      data-testid={`data-row-action-${action.id}-${row.id}`}
                    >
                      {action.label}
                    </span>
                  ))}
                </div>
              )}
            </button>
          )
        })}
      </div>

      {hasColumnActions && (
        <div className="grid gap-1 sm:hidden">
          {columns.filter((column) => actionsForTarget(columnActions, column.id).length > 0).map((column) => (
            <div
              key={column.id}
              className="flex items-center justify-between gap-2 rounded border border-ink/10 bg-paper/70 px-2 py-1 text-xs"
            >
              <span className="font-semibold text-ink/62">{column.label}</span>
              <span className="flex flex-wrap justify-end gap-1">
                {actionsForTarget(columnActions, column.id).map((action) => (
                  <button
                    key={action.id}
                    type="button"
                    onClick={() => onColumnAction?.(action.id, column.id)}
                    className="rounded border border-ink/10 bg-bg/80 px-2 py-1 text-[10px] font-semibold text-ink/62"
                    data-testid={`data-column-action-${action.id}-${column.id}`}
                  >
                    {action.label}
                  </button>
                ))}
              </span>
            </div>
          ))}
        </div>
      )}

      {hiddenCount > 0 && (
        <p className="text-xs text-ink/48">Еще {hiddenCount} строк скрыто в компактном режиме.</p>
      )}
    </div>
  )
}
