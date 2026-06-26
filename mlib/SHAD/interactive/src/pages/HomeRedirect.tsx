import { Navigate } from 'react-router-dom'

export function HomeRedirect() {
  return <Navigate to="/algebra/linear-maps/kernel" replace />
}
