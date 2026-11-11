import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import SurveyForm from "../components/SurveyForm";
import type { AnswerPayload } from "../components/SurveyForm";
import { ErrorBox } from "../components/ui";
import { api } from "../lib/api";
import type { Question } from "../lib/types";

export default function SelfAssessmentPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let cancelled = false;
    api<Question[]>(`/assessments/${id}/questions`)
      .then((q) => {
        if (!cancelled) setQuestions(q);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  async function submit(answers: AnswerPayload[]) {
    await api(`/assessments/${id}/self-response`, { method: "POST", body: { answers } });
    navigate(`/assessments/${id}`);
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Link to={`/assessments/${id}`} className="text-sm text-indigo-600 underline">
        ← Back
      </Link>
      <h1 className="text-xl font-semibold">Rate yourself</h1>
      <p className="text-sm text-gray-600">
        Be honest — your self-rating is compared with how others see you.
      </p>
      <ErrorBox error={error} />
      {!questions && !error && <p className="text-gray-500">Loading…</p>}
      {questions && <SurveyForm questions={questions} submitLabel="Submit self-assessment" onSubmit={submit} />}
    </div>
  );
}
