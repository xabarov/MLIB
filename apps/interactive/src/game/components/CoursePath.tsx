import { ChevronRight } from 'lucide-react'
import type { CourseMapNode } from '../courseMap'

type CoursePathProps = {
  nodes: CourseMapNode[]
  recommendedMissionId: string
}

export function CoursePath({ nodes, recommendedMissionId }: CoursePathProps) {
  return (
    <div
      className="flex gap-2 overflow-x-auto rounded-md border border-ink/10 bg-paper/78 p-2"
      data-testid="course-path"
    >
      {nodes.map((node, index) => {
        const current = node.mission.id === recommendedMissionId
        return (
          <div key={node.id} className="flex shrink-0 items-center gap-2">
            <span
              className={`inline-flex items-center rounded px-3 py-2 text-xs font-semibold ${
                current ? 'bg-orange text-bg' : 'bg-bg text-ink/68'
              }`}
            >
              {node.mission.title}
            </span>
            {index < nodes.length - 1 && <ChevronRight className="size-4 text-ink/35" />}
          </div>
        )
      })}
    </div>
  )
}
