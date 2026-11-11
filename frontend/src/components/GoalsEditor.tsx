import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../lib/api";
import type { Goal } from "../lib/types";
import { Button, ErrorBox } from "./ui";

type Draft = { title: string; description: string; due_date: string; status: Goal["status"] };

function toDraft(goal?: Goal): Draft {
  return goal
    ? { title: goal.title, description: goal.description ?? "", due_date: goal.due_date, status: goal.status }
    : { title: "", description: "", due_date: "", status: "not_started" };
}

const inputClass =
  "w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none";

export default function GoalsEditor({ assessmentId, initial }: { assessmentId: string; initial: Goal[] }) {
  const [drafts, setDrafts] = useState<Draft[]>(() => [toDraft(initial[0]), toDraft(initial[1])]);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  function update(index: number, patch: Partial<Draft>) {
    setDrafts((all) => all.map((d, i) => (i === index ? { ...d, ...patch } : d)));
    setSaved(false);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const goals = drafts
      .filter((d) => d.title.trim())
      .map((d) => ({
        title: d.title.trim(),
        description: d.description.trim() || null,
        due_date: d.due_date,
        status: d.status,
      }));
    setBusy(true);
    setError(null);
    try {
      await api<Goal[]>(`/assessments/${assessmentId}/goals`, { method: "PUT", body: { goals } });
      setSaved(true);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {drafts.map((d, i) => (
        <fieldset key={i} className="space-y-3 rounded-md border border-gray-200 p-4">
          <legend className="px-1 text-sm font-medium">Commitment {i + 1}{i === 1 && " (optional)"}</legend>
          <label className="block text-sm">
            <span className="mb-1 block text-gray-700">What will you do?</span>
            <input className={inputClass} maxLength={200} required={i === 0} value={d.title} onChange={(e) => update(i, { title: e.target.value })} />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-gray-700">Details (optional)</span>
            <textarea className={inputClass} rows={2} maxLength={1000} value={d.description} onChange={(e) => update(i, { description: e.target.value })} />
          </label>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm">
              <span className="mb-1 block text-gray-700">Due date</span>
              <input type="date" className={inputClass} required={!!d.title.trim()} value={d.due_date} onChange={(e) => update(i, { due_date: e.target.value })} />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block text-gray-700">Status</span>
              <select className={inputClass} value={d.status} onChange={(e) => update(i, { status: e.target.value as Goal["status"] })}>
                <option value="not_started">Not started</option>
                <option value="in_progress">In progress</option>
                <option value="done">Done</option>
              </select>
            </label>
          </div>
        </fieldset>
      ))}
      <ErrorBox error={error} />
      <div className="flex items-center gap-3">
        <Button type="submit" disabled={busy}>{busy ? "Saving…" : "Save commitments"}</Button>
        {saved && <span className="text-sm text-green-700">Saved ✓</span>}
      </div>
    </form>
  );
}
