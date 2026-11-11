import { useState } from "react";
import type { FormEvent } from "react";
import type { Question } from "../lib/types";
import { Button, ErrorBox } from "./ui";

export type AnswerPayload = { question_id: string; score: number };

type Props = {
  questions: Question[];
  submitLabel: string;
  onSubmit: (answers: AnswerPayload[]) => Promise<void>;
};

export default function SurveyForm({ questions, submitLabel, onSubmit }: Props) {
  const [scores, setScores] = useState<Record<string, number>>({});
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  const answered = questions.filter((q) => scores[q.id] !== undefined).length;
  const complete = answered === questions.length;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!complete) return;
    setBusy(true);
    setError(null);
    try {
      await onSubmit(questions.map((q) => ({ question_id: q.id, score: scores[q.id] })));
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="sticky top-0 z-10 -mx-4 bg-gray-50/95 px-4 py-3 backdrop-blur">
        <p className="text-sm text-gray-700">
          {answered} of {questions.length} answered
        </p>
        <div className="mt-2 h-2 rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-indigo-600 transition-all"
            style={{ width: `${(answered / questions.length) * 100}%` }}
          />
        </div>
      </div>

      <p className="text-sm text-gray-600">
        Rate each behaviour from <b>1</b> (rarely) to <b>5</b> (consistently).
      </p>

      {questions.map((q) => (
        <div key={q.id} className="rounded-lg border border-gray-200 bg-white p-4">
          <fieldset>
            <legend className="font-medium">
              <span className="mr-1 text-gray-400">{q.position}.</span>
              {q.text}
            </legend>
            <p className="mt-1 text-xs uppercase tracking-wide text-gray-500">{q.category}</p>
            <div className="mt-3 flex gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <label key={n} className="flex-1">
                  <input
                    type="radio"
                    name={q.id}
                    value={n}
                    checked={scores[q.id] === n}
                    onChange={() => setScores((s) => ({ ...s, [q.id]: n }))}
                    className="peer sr-only"
                  />
                  <span className="flex h-11 cursor-pointer items-center justify-center rounded-md border border-gray-300 text-sm font-medium peer-checked:border-indigo-600 peer-checked:bg-indigo-600 peer-checked:text-white peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-400">
                    {n}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
        </div>
      ))}

      <ErrorBox error={error} />
      <Button type="submit" disabled={!complete || busy} className="w-full sm:w-auto">
        {busy ? "Submitting…" : submitLabel}
      </Button>
      {!complete && <p className="text-xs text-gray-500">Answer all questions to submit.</p>}
    </form>
  );
}
