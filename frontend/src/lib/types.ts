export type User = { id: string; name: string; email: string; created_at: string };

export type Assessment = {
  id: string;
  title: string;
  status: "draft" | "open" | "closed";
  min_responses: number;
  closes_at: string | null;
  closed_at: string | null;
  self_completed_at: string | null;
  created_at: string;
  rater_response_count: number;
};

export type AssessmentStatus = {
  id: string;
  status: "draft" | "open" | "closed";
  closes_at: string | null;
  closed_at: string | null;
  min_responses: number;
  invitation_count: number;
  rater_response_count: number;
  self_completed: boolean;
  results_unlocked: boolean;
};

export type Question = { id: string; category: string; text: string; position: number };

export type InvitationLink = {
  id: string;
  rater_email: string;
  invite_url: string;
  expires_at: string;
};

export type GuestSurvey = {
  assessment_title: string;
  leader_name: string;
  expires_at: string;
  questions: Question[];
};

export type ScoreTriple = { self_score: number | null; others_mean: number; gap: number | null };
export type CategoryResult = ScoreTriple & { category: string };
export type ItemResult = ScoreTriple & {
  question_id: string;
  position: number;
  category: string;
  text: string;
};

export type Results = {
  assessment_id: string;
  title: string;
  rater_response_count: number;
  overall: ScoreTriple;
  categories: CategoryResult[];
  items: ItemResult[];
  focus_areas: ItemResult[];
  focus_note: string;
};

export type Goal = {
  id: string;
  title: string;
  description: string | null;
  due_date: string;
  status: "not_started" | "in_progress" | "done";
  created_at: string;
};
