import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";
import { ApiError } from "../lib/api";

export function Button({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}

export function Field({ label, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium text-gray-700">{label}</span>
      <input
        className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
        {...props}
      />
    </label>
  );
}

export function Card({ children }: { children: ReactNode }) {
  return <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">{children}</div>;
}

export function ErrorBox({ error }: { error: unknown }) {
  if (!error) return null;
  const message =
    error instanceof ApiError ? error.message : "Something went wrong. Is the backend running?";
  const details = error instanceof ApiError ? error.details : [];
  return (
    <div role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700">
      <p>{message}</p>
      {details.length > 0 && (
        <ul className="mt-1 list-disc pl-5">
          {details.map((d) => (
            <li key={d.field}>
              {d.field}: {d.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
