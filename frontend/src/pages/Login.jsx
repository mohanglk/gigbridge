import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setError("");

    // NOTE: no backend auth endpoint exists yet, so for now we check
    // against the profile saved in localStorage during registration.
    // Swap this for a real POST /api/auth/login call once the backend
    // is ready.
    const stored = localStorage.getItem("gb_profile");
    if (!stored) {
      setError("No account found. Please register first.");
      return;
    }

    const profile = JSON.parse(stored);
    if (profile.email === form.email && profile.password === form.password) {
      localStorage.setItem("gb_logged_in", "true");
      navigate("/profile");
    } else {
      setError("Invalid email or password. Please try again.");
    }
  }

  return (
    <AuthLayout title="LOG IN" subtitle="Welcome back to GigBridge.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block text-[13px] font-semibold text-ink-soft mb-1.5">
            Email
          </label>
          <input
            type="email"
            required
            value={form.email}
            onChange={update("email")}
            className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-[13px] font-semibold text-ink-soft mb-1.5">
            Password
          </label>
          <input
            type="password"
            required
            value={form.password}
            onChange={update("password")}
            className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
            placeholder="••••••••"
          />
        </div>

        {error && <p className="text-[13px] text-orange-deep">{error}</p>}

        <button
          type="submit"
          className="mt-2 bg-ink text-paper font-semibold text-[14.5px] py-3 rounded-sm"
        >
          Log in
        </button>
      </form>

      <p className="text-[13.5px] text-ink-soft mt-6 text-center">
        Don&apos;t have an account?{" "}
        <Link to="/register" className="font-semibold text-orange-deep">
          Sign up
        </Link>
      </p>
    </AuthLayout>
  );
}
