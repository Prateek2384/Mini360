import { useAuth } from "../auth/useAuth";

export default function DashboardPage() {
  const { user } = useAuth();
  return <h1 className="text-xl font-semibold">Welcome, {user?.name}</h1>;
}
