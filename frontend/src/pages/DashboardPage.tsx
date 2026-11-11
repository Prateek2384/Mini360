import { useEffect, useState } from "react";
import { Link } from "react-router";
import { Card, ErrorBox, StatusBadge } from "../components/ui";
import { api } from "../lib/api";
import { formatDate } from "../lib/format";
import type { Assessment } from "../lib/types";

export default function DashboardPage() {
  const [items, setItems] = useState<Assessment[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    api<Assessment[]>("/assessments").then(setItems).catch(setError);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Your assessments</h1>
        <Link
          to="/assessments/new"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          New assessment
        </Link>
      </div>

      <ErrorBox error={error} />
      {items === null && !error && <p className="text-gray-500">Loading…</p>}
      {items?.length === 0 && (
        <Card>
          <p className="text-gray-600">No assessments yet. Create one to start collecting feedback.</p>
        </Card>
      )}

      <ul className="space-y-3">
        {items?.map((a) => (
          <li key={a.id}>
            <Link
              to={`/assessments/${a.id}`}
              className="block rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:border-indigo-300"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="font-medium">{a.title}</span>
                <StatusBadge status={a.status} />
              </div>
              <p className="mt-1 text-sm text-gray-600">
                {a.rater_response_count} of {a.min_responses} responses · closes {formatDate(a.closes_at)}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
