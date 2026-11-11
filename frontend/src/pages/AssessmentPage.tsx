import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router";
import { Button, Card, ErrorBox, Field, StatusBadge } from "../components/ui";
import { api } from "../lib/api";
import { defaultCloseInput, formatDate, localInputToIso, toLocalInput } from "../lib/format";
import type { Assessment, AssessmentStatus, InvitationLink } from "../lib/types";

export default function AssessmentPage() {
  const { id } = useParams();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [status, setStatus] = useState<AssessmentStatus | null>(null);
  const [error, setError] = useState<unknown>(null);

  const [reloadKey, setReloadKey] = useState(0);
  const reload = () => setReloadKey((k) => k + 1);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      api<Assessment[]>("/assessments"),
      api<AssessmentStatus>(`/assessments/${id}/status`),
    ])
      .then(([list, st]) => {
        if (cancelled) return;
        setAssessment(list.find((a) => a.id === id) ?? null);
        setStatus(st);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      });
    return () => {
      cancelled = true;
    };
  }, [id, reloadKey]);

  if (error) return <ErrorBox error={error} />;
  if (!assessment || !status || !id) return <p className="text-gray-500">Loading…</p>;

  const lockMessage =
    status.rater_response_count < status.min_responses
      ? `Results unlock after ${status.min_responses} responses. (${status.rater_response_count} of ${status.min_responses} received)`
      : `Results unlock when the survey closes on ${formatDate(status.closes_at)}.`;

  return (
    <div className="space-y-6">
      <Link to="/" className="text-sm text-indigo-600 underline">← All assessments</Link>

      <Card>
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-xl font-semibold">{assessment.title}</h1>
          <StatusBadge status={status.status} />
        </div>
        <dl className="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
          <Stat label="Closes" value={formatDate(status.closes_at)} />
          <Stat label="Invited" value={String(status.invitation_count)} />
          <Stat label="Responses" value={`${status.rater_response_count} / ${status.min_responses}`} />
          <Stat label="Self-assessment" value={status.self_completed ? "Done" : "Pending"} />
        </dl>
      </Card>

      {status.status === "draft" && <LaunchBox id={id} initial={status.closes_at} onDone={reload} />}

      <Card>
        <h2 className="font-semibold">Your self-assessment</h2>
        {status.self_completed ? (
          <p className="mt-2 text-sm text-green-700">✓ Completed</p>
        ) : status.status === "closed" ? (
          <p className="mt-2 text-sm text-gray-600">The survey has closed.</p>
        ) : (
          <Link to={`/assessments/${id}/self`} className="mt-3 inline-block rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500">
            Rate yourself (10 questions)
          </Link>
        )}
      </Card>

      {status.status === "open" && <InviteBox id={id} onDone={reload} />}

      <Card>
        <h2 className="font-semibold">Results</h2>
        {status.results_unlocked ? (
          <Link to={`/assessments/${id}/results`} className="mt-3 inline-block rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500">
            View results
          </Link>
        ) : (
          <p className="mt-2 text-sm text-gray-600">{lockMessage}</p>
        )}
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}

function LaunchBox({ id, initial, onDone }: { id: string; initial: string | null; onDone: () => void }) {
  const [closesAt, setClosesAt] = useState(initial ? toLocalInput(new Date(initial)) : defaultCloseInput());
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api(`/assessments/${id}/launch`, { method: "POST", body: { closes_at: localInputToIso(closesAt) } });
      onDone();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <h2 className="font-semibold">Launch</h2>
      <p className="mt-1 text-sm text-gray-600">Once launched, you can invite raters.</p>
      <form onSubmit={onSubmit} className="mt-4 space-y-3">
        <Field label="Survey closes" type="datetime-local" required value={closesAt} onChange={(e) => setClosesAt(e.target.value)} />
        <ErrorBox error={error} />
        <Button type="submit" disabled={busy}>{busy ? "Launching…" : "Launch survey"}</Button>
      </form>
    </Card>
  );
}

function InviteBox({ id, onDone }: { id: string; onDone: () => void }) {
  const [text, setText] = useState("");
  const [links, setLinks] = useState<InvitationLink[]>([]);
  const [copied, setCopied] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const emails = text.split(/[\s,;]+/).map((s) => s.trim()).filter(Boolean);
    if (emails.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api<{ invitations: InvitationLink[] }>(`/assessments/${id}/invitations`, {
        method: "POST",
        body: { emails },
      });
      setLinks((prev) => [...res.invitations, ...prev]);
      setText("");
      onDone();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function copy(url: string) {
    await navigator.clipboard.writeText(url);
    setCopied(url);
  }

  return (
    <Card>
      <h2 className="font-semibold">Invite raters</h2>
      <p className="mt-1 text-sm text-gray-600">Invite at least 3 colleagues. They don't need an account.</p>
      <form onSubmit={onSubmit} className="mt-4 space-y-3">
        <label className="block text-sm">
          <span className="mb-1 block font-medium text-gray-700">Email addresses (comma or new line separated)</span>
          <textarea
            rows={3}
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
            placeholder={"amit@example.com\nneha@example.com\npriya@example.com"}
          />
        </label>
        <ErrorBox error={error} />
        <Button type="submit" disabled={busy}>{busy ? "Creating links…" : "Create invitation links"}</Button>
      </form>

      {links.length > 0 && (
        <div className="mt-5 space-y-2">
          <p className="rounded-md bg-amber-50 p-3 text-sm text-amber-800">
            Copy these links now and send them to each person. For security, they are shown only once.
          </p>
          <ul className="space-y-2">
            {links.map((l) => (
              <li key={l.id} className="flex flex-col gap-2 rounded-md border border-gray-200 p-3 sm:flex-row sm:items-center sm:justify-between">
                <span className="text-sm font-medium">{l.rater_email}</span>
                <button
                  type="button"
                  onClick={() => void copy(l.invite_url)}
                  className="rounded-md border border-gray-300 px-3 py-1 text-sm hover:bg-gray-50"
                >
                  {copied === l.invite_url ? "Copied ✓" : "Copy link"}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
