import { useEffect, useState } from "react";
import { useParams } from "react-router";
import SurveyForm from "../components/SurveyForm";
import type { AnswerPayload } from "../components/SurveyForm";
import { Card } from "../components/ui";
import { ApiError, api } from "../lib/api";
import { formatDate } from "../lib/format";
import type { GuestSurvey } from "../lib/types";

type State =
  | { kind: "loading" }
  | { kind: "ready"; survey: GuestSurvey }
  | { kind: "done" }
  | { kind: "error"; title: string; message: string };

function toErrorState(err: unknown): State {
  if (err instanceof ApiError) {
    if (err.status === 404)
      return { kind: "error", title: "Link not valid", message: "Please check that you copied the full invitation link." };
    if (err.status === 409)
      return { kind: "error", title: "Already submitted", message: "Feedback has already been submitted with this link. Thank you!" };
    if (err.status === 410)
      return { kind: "error", title: "Survey closed", message: "This invitation has expired or the survey has closed." };
  }
  return { kind: "error", title: "Something went wrong", message: "Please try again later." };
}

export default function GuestSurveyPage() {
  const { token = "" } = useParams();
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    api<GuestSurvey>(`/invitations/${encodeURIComponent(token)}`)
      .then((survey) => {
        if (!cancelled) setState({ kind: "ready", survey });
      })
      .catch((err) => {
        if (!cancelled) setState(toErrorState(err));
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function submit(answers: AnswerPayload[]) {
    await api(`/invitations/${encodeURIComponent(token)}/submit`, { method: "POST", body: { answers } });
    setState({ kind: "done" });
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-2xl space-y-4">
        <p className="font-semibold text-indigo-700">Mini 360</p>

        {state.kind === "loading" && <p className="text-gray-500">Loading…</p>}

        {state.kind === "error" && (
          <Card>
            <h1 className="text-lg font-semibold">{state.title}</h1>
            <p className="mt-2 text-gray-600">{state.message}</p>
          </Card>
        )}

        {state.kind === "done" && (
          <Card>
            <h1 className="text-lg font-semibold">Thank you!</h1>
            <p className="mt-2 text-gray-600">
              Your feedback has been submitted anonymously. You can close this page.
            </p>
          </Card>
        )}

        {state.kind === "ready" && (
          <>
            <Card>
              <h1 className="text-lg font-semibold">
                {state.survey.leader_name} has asked for your feedback
              </h1>
              <p className="mt-1 text-sm text-gray-600">“{state.survey.assessment_title}”</p>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-gray-600">
                <li>10 short questions, about 3 minutes.</li>
                <li>
                  {state.survey.leader_name} only sees averages from at least 3 people — never your
                  individual answers.
                </li>
                <li>This link works once and closes on {formatDate(state.survey.expires_at)}.</li>
              </ul>
            </Card>
            <SurveyForm questions={state.survey.questions} submitLabel="Submit feedback" onSubmit={submit} />
          </>
        )}
      </div>
    </div>
  );
}
