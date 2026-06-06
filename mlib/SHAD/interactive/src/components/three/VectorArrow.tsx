import { Line } from '@react-three/drei'

type VectorArrowProps = {
  vector: readonly [number, number, number]
  color: string
  label?: string
  lineWidth?: number
}

export function VectorArrow({ vector, color, lineWidth = 4 }: VectorArrowProps) {
  const end: [number, number, number] = [vector[0], vector[1], vector[2]]

  return (
    <group>
      <Line points={[[0, 0, 0], end]} color={color} lineWidth={lineWidth} />
      <mesh position={end}>
        <sphereGeometry args={[0.08, 18, 18]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  )
}
