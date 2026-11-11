import { Navigate, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";

export default function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-8 text-gray-500">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
