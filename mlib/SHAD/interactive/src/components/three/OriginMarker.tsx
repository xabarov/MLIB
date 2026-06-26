import { tokens } from '../../theme/tokens'

type OriginMarkerProps = {
  color?: string
  size?: number
}

export function OriginMarker({ color = tokens.ink, size = 0.08 }: OriginMarkerProps) {
  return (
    <mesh position={[0, 0, 0]}>
      <sphereGeometry args={[size, 16, 16]} />
      <meshStandardMaterial color={color} />
    </mesh>
  )
}
