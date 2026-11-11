import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import GoalsEditor from "../components/GoalsEditor";
import { Card, ErrorBox } from "../components/ui";
import { api, apiUrl } from "../lib/api";
import { formatGap, formatScore } from "../lib/format";
import type { Goal, Results } from "../lib/types";

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

export default function ResultsPage() {
  const { id } = useParams();
  const [data, setData] = useState<{ results: Results; goals: Goal[] } | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api<Results>(`/assessments/${id}/results`), api<Goal[]>(`/assessments/${id}/goals`)])
      .then(([results, goals]) => {
        if (!cancelled) setData({ results, goals });
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const back = (
    <Link to={`/assessments/${id}`} className="text-sm text-indigo-600 underline">
      ← Back to assessment
    </Link>
  );

  if (error)
    return (
      <div className="space-y-4">
        {back}
        <ErrorBox error={error} />
      </div>
    );
  if (!data || !id) return <p className="text-gray-500">Loading…</p>;

  const { results, goals } = data;
  const weakest = [...results.categories].sort((a, b) => a.others_mean - b.others_mean).slice(0, 2);

  return (
    <div className="space-y-6">
      {back}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold">{results.title}</h1>
          <p className="text-sm text-gray-600">Based on {results.rater_response_count} anonymous responses</p>
        </div>
        <a
          href={apiUrl(`/assessments/${id}/report.pdf`)}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-center text-sm font-medium hover:bg-gray-50"
        >
          Download PDF
        </a>
      </div>

      <Card>
        <h2 className="font-semibold">Overall</h2>
        <div className="mt-4 grid grid-cols-3 gap-3 text-center">
          <Score label="You" value={formatScore(results.overall.self_score)} />
          <Score label="Others" value={formatScore(results.overall.others_mean)} />
          <Score label="Gap" value={formatGap(results.overall.gap)} />
        </div>
        <p className="mt-3 text-xs text-gray-500">
          Gap = your rating minus others' average. Positive means you rated yourself higher.
        </p>
      </Card>

      <Card>
        <h2 className="font-semibold">By category</h2>
        <div className="mt-4 space-y-5">
          {results.categories.map((c) => (
            <div key={c.category}>
              <div className="flex justify-between text-sm">
                <span className="font-medium">{capitalize(c.category)}</span>
                <span className="text-gray-600">Gap {formatGap(c.gap)}</span>
              </div>
              <div className="mt-2 space-y-1">
                <Bar label="You" value={c.self_score} color="bg-indigo-300" />
                <Bar label="Others" value={c.others_mean} color="bg-indigo-600" />
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h2 className="font-semibold">Areas to improve</h2>
        <p className="mt-2">
          Focus on improving <b>{weakest.map((c) => capitalize(c.category)).join(" and ")}</b>.
        </p>
        {/* FR-07: two lowest-rated behaviours. Remove this block if not needed. */}
        <p className="mt-4 text-sm font-medium text-gray-700">Lowest-rated behaviours</p>
        <ul className="mt-1 space-y-1 text-sm">
          {results.focus_areas.map((f) => (
            <li key={f.question_id} className="flex justify-between gap-3">
              <span>{f.text}</span>
              <span className="font-medium">{formatScore(f.others_mean)}</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs italic text-gray-500">{results.focus_note}</p>
      </Card>

      <Card>
        <details>
          <summary className="cursor-pointer font-semibold">All behaviours</summary>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-gray-500">
                <tr>
                  <th className="py-2 pr-3">Behaviour</th>
                  <th className="py-2 pr-3">You</th>
                  <th className="py-2 pr-3">Others</th>
                  <th className="py-2">Gap</th>
                </tr>
              </thead>
              <tbody>
                {results.items.map((item) => (
                  <tr key={item.question_id} className="border-t border-gray-100">
                    <td className="py-2 pr-3">{item.text}</td>
                    <td className="py-2 pr-3">{formatScore(item.self_score)}</td>
                    <td className="py-2 pr-3">{formatScore(item.others_mean)}</td>
                    <td className="py-2">{formatGap(item.gap)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </Card>

      <Card>
        <h2 className="font-semibold">Development commitments</h2>
        <p className="mt-1 text-sm text-gray-600">Turn your results into up to two concrete actions.</p>
        <div className="mt-4">
          <GoalsEditor assessmentId={id} initial={goals} />
        </div>
      </Card>
    </div>
  );
}

function Score({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-gray-50 p-3">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  );
}

function Bar({ label, value, color }: { label: string; value: number | null; color: string }) {
  const pct = value === null ? 0 : (value / 5) * 100;
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-14 shrink-0 text-gray-500">{label}</span>
      <div className="h-3 flex-1 rounded-full bg-gray-100">
        <div className={`h-3 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-8 text-right font-medium">{formatScore(value)}</span>
    </div>
  );
}
