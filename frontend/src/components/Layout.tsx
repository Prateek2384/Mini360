import { Link, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";

export default function Layout() {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <Link to="/" className="font-semibold text-indigo-700">
            Mini 360
          </Link>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-gray-600">{user?.name}</span>
            <button onClick={() => void logout()} className="text-gray-700 underline">
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
