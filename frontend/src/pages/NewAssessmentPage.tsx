import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router";
import { Button, Card, ErrorBox, Field } from "../components/ui";
import { api } from "../lib/api";
import { defaultCloseInput, localInputToIso } from "../lib/format";
import type { Assessment } from "../lib/types";

export default function NewAssessmentPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [closesAt, setClosesAt] = useState(defaultCloseInput());
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function create(launch: boolean) {
    setBusy(true);
    setError(null);
    try {
      const a = await api<Assessment>("/assessments", {
        method: "POST",
        body: { title, closes_at: localInputToIso(closesAt) },
      });
      if (launch) {
        try {
          await api(`/assessments/${a.id}/launch`, { method: "POST" });
        } catch {
          // Draft stays; the assessment page shows a Launch button.
        }
      }
      navigate(`/assessments/${a.id}`);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void create(true);
  }

  return (
    <div className="mx-auto max-w-lg space-y-4">
      <h1 className="text-xl font-semibold">New assessment</h1>
      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <Field label="Title" required maxLength={200} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Q4 leadership check-in" />
          <Field label="Survey closes" type="datetime-local" required value={closesAt} onChange={(e) => setClosesAt(e.target.value)} />
          <p className="text-xs text-gray-500">
            Raters can respond until this time. Results unlock after it passes and at least 3 people have responded.
          </p>
          <ErrorBox error={error} />
          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={busy}>
              {busy ? "Creating…" : "Create & launch"}
            </Button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void create(false)}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Save as draft
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}
