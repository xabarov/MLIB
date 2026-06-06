import { Line, Text } from '@react-three/drei'
import { tokens } from '../../theme/tokens'

type AxesGridProps = {
  limit?: number
}

export function AxesGrid({ limit = 2.2 }: AxesGridProps) {
  const axisColor = tokens.gray
  const labelColor = tokens.ink
  const tick = 0.5

  const ticks = Array.from(
    { length: Math.floor((limit * 2) / tick) + 1 },
    (_, i) => -limit + i * tick,
  ).filter((v) => Math.abs(v) > 1e-6)

  return (
    <group>
      <Line points={[[-limit, 0, 0], [limit, 0, 0]]} color={axisColor} lineWidth={1} />
      <Line points={[[0, -limit, 0], [0, limit, 0]]} color={axisColor} lineWidth={1} />
      <Line points={[[0, 0, -limit], [0, 0, limit]]} color={axisColor} lineWidth={1} />

      <Text position={[limit + 0.15, 0, 0]} fontSize={0.22} color={labelColor} anchorX="left">
        x
      </Text>
      <Text position={[0, limit + 0.15, 0]} fontSize={0.22} color={labelColor} anchorX="center">
        y
      </Text>
      <Text position={[0, 0, limit + 0.25]} fontSize={0.22} color={labelColor} anchorX="center">
        z
      </Text>

      {ticks.map((v) => (
        <group key={`tick-${v}`}>
          <Line
            points={[
              [v, -0.06, 0],
              [v, 0.06, 0],
            ]}
            color={axisColor}
            lineWidth={0.5}
            transparent
            opacity={0.5}
          />
          <Line
            points={[
              [0, v, -0.06],
              [0, v, 0.06],
            ]}
            color={axisColor}
            lineWidth={0.5}
            transparent
            opacity={0.5}
          />
          <Line
            points={[
              [-0.06, 0, v],
              [0.06, 0, v],
            ]}
            color={axisColor}
            lineWidth={0.5}
            transparent
            opacity={0.5}
          />
        </group>
      ))}
    </group>
  )
}
