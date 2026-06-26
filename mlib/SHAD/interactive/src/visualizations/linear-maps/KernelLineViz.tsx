import { useState } from 'react'
import type { ThreeEvent } from '@react-three/fiber'
import { AxesGrid } from '../../components/three/AxesGrid'
import { CameraController } from '../../components/three/CameraController'
import { LabeledLine } from '../../components/three/LabeledLine'
import { OriginMarker } from '../../components/three/OriginMarker'
import { SceneCanvas } from '../../components/three/SceneCanvas'
import { SemiTransparentPlane } from '../../components/three/SemiTransparentPlane'
import { VectorArrow } from '../../components/three/VectorArrow'
import { useSceneStore } from '../../store/sceneStore'
import { tokens } from '../../theme/tokens'
import { kernelLineConfig } from './kernelLineConfig'

type KernelLineVizProps = {
  candidate?: readonly [number, number, number]
  projection?: readonly [number, number, number]
  onCandidateChange?: (candidate: [number, number, number]) => void
}

function snapDragCoord(value: number): number {
  return Math.max(-3, Math.min(3, Math.round(value / 0.25) * 0.25))
}

function DraggableCandidateHandle({
  candidate,
  onCandidateChange,
}: {
  candidate: readonly [number, number, number]
  onCandidateChange: (candidate: [number, number, number]) => void
}) {
  const [dragging, setDragging] = useState(false)

  const updateFromPoint = (event: ThreeEvent<PointerEvent>) => {
    onCandidateChange([
      snapDragCoord(event.point.x),
      snapDragCoord(event.point.y),
      candidate[2],
    ])
  }

  return (
    <group>
      <mesh
        position={[0, 0, candidate[2]]}
        onPointerMove={(event) => {
          if (!dragging) return
          updateFromPoint(event)
        }}
        onPointerUp={() => setDragging(false)}
        onPointerCancel={() => setDragging(false)}
      >
        <planeGeometry args={[8, 8]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
      <mesh position={[0, 0, candidate[2] - 0.003]}>
        <circleGeometry args={[1.85, 48]} />
        <meshBasicMaterial color={tokens.energy} transparent opacity={0.07} depthWrite={false} />
      </mesh>
      <mesh
        position={candidate}
        onPointerDown={(event) => {
          event.stopPropagation()
          setDragging(true)
        }}
        onPointerUp={() => setDragging(false)}
        onPointerCancel={() => setDragging(false)}
      >
        <sphereGeometry args={[0.16, 24, 24]} />
        <meshStandardMaterial color={tokens.energy} emissive={tokens.energy} emissiveIntensity={0.15} />
      </mesh>
    </group>
  )
}

export function KernelLineViz({ candidate, projection, onCandidateChange }: KernelLineVizProps) {
  const showPlane = useSceneStore((s) => s.showAuxiliaryPlane)
  const cfg = kernelLineConfig

  return (
    <SceneCanvas>
      <CameraController
        distance={cfg.camera.distance}
        elevDeg={cfg.camera.elevDeg}
        azimDeg={cfg.camera.azimDeg}
      />
      <AxesGrid limit={cfg.axisLimit} />
      <OriginMarker color={cfg.colors.origin} />
      <LabeledLine
        direction={cfg.direction}
        tMin={cfg.tMin}
        tMax={cfg.tMax}
        color={cfg.colors.line}
        lineWidth={7}
        label="ker φ"
        labelAt={cfg.labelPosition}
      />
      {showPlane && (
        <SemiTransparentPlane
          fn={cfg.planeFn}
          extent={cfg.planeExtent}
          steps={cfg.planeGridSteps}
          color={cfg.colors.plane}
          opacity={cfg.colors.planeOpacity}
        />
      )}
      {projection && (
        <VectorArrow vector={projection} color={tokens.target} label="proj" lineWidth={4.5} />
      )}
      {candidate && projection && (
        <VectorArrow
          vector={[
            candidate[0] - projection[0],
            candidate[1] - projection[1],
            candidate[2] - projection[2],
          ]}
          color={tokens.danger}
          label="err"
          lineWidth={2.5}
        />
      )}
      {candidate && (
        <VectorArrow vector={candidate} color={tokens.energy} label="x" lineWidth={8} />
      )}
      {candidate && onCandidateChange && (
        <DraggableCandidateHandle candidate={candidate} onCandidateChange={onCandidateChange} />
      )}
    </SceneCanvas>
  )
}
