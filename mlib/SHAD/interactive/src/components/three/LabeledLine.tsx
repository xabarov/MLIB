import { Line, Text } from '@react-three/drei'

type LabeledLineProps = {
  direction: readonly [number, number, number]
  tMin: number
  tMax: number
  color: string
  lineWidth?: number
  label?: string
  labelAt?: readonly [number, number, number]
}

export function LabeledLine({
  direction,
  tMin,
  tMax,
  color,
  lineWidth = 3,
  label,
  labelAt,
}: LabeledLineProps) {
  const [dx, dy, dz] = direction
  const start: [number, number, number] = [dx * tMin, dy * tMin, dz * tMin]
  const end: [number, number, number] = [dx * tMax, dy * tMax, dz * tMax]

  return (
    <group>
      <Line points={[start, end]} color={color} lineWidth={lineWidth} />
      {label && labelAt && (
        <Text position={[...labelAt]} fontSize={0.28} color={color} anchorX="center">
          {label}
        </Text>
      )}
    </group>
  )
}
