import { Navigate, Route, Routes } from "react-router";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import AssessmentPage from "./pages/AssessmentPage";
import DashboardPage from "./pages/DashboardPage";
import GuestSurveyPage from "./pages/GuestSurveyPage";
import LoginPage from "./pages/LoginPage";
import NewAssessmentPage from "./pages/NewAssessmentPage";
import RegisterPage from "./pages/RegisterPage";
import SelfAssessmentPage from "./pages/SelfAssessmentPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/invite/:token" element={<GuestSurveyPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/assessments/new" element={<NewAssessmentPage />} />
          <Route path="/assessments/:id" element={<AssessmentPage />} />
          <Route path="/assessments/:id/self" element={<SelfAssessmentPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
