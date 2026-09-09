import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { api } from "../api/client";

export default function Register() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialType =
    searchParams.get("type") === "venue" ? "venue" : "musician";

  const [accountType, setAccountType] = useState(initialType);
  const [form, setForm] = useState({
    name: "",
    identityName: "", // stage/band name (musician) or venue name (venue)
    email: "",
    phone: "",
    city: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (accountType === "venue" && !form.identityName.trim()) {
      setError("Venue name is required.");
      return;
    }

    setLoading(true);
    try {
      // Expects backend endpoint: POST /api/auth/register
      // body includes accountType so the backend creates a Musician or Venue record
      const data = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ ...form, accountType }),
      });
      localStorage.setItem("gb_token", data.token);
      // Send them straight into completing their profile (instruments/genres,
      // or venue capacity/type) since we only collected the basics here.
      navigate("/onboarding");
    } catch (err) {
      setError("Something went wrong creating your account. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="CREATE ACCOUNT"
      subtitle="Join GigBridge as a musician or a venue."
    >
      {/* account type toggle */}
      <div className="grid grid-cols-2 gap-2 mb-7">
        <button
          type="button"
          onClick={() => setAccountType("musician")}
          className={`text-[13.5px] font-semibold py-2.5 rounded-sm border-[1.5px] ${
            accountType === "musician"
              ? "bg-orange-deep text-paper border-orange-deep"
              : "bg-transparent text-ink-soft border-ink/25"
          }`}
        >
          I&apos;m a Musician
        </button>
        <button
          type="button"
          onClick={() => setAccountType("venue")}
          className={`text-[13.5px] font-semibold py-2.5 rounded-sm border-[1.5px] ${
            accountType === "venue"
              ? "bg-teal-deep text-paper border-teal-deep"
              : "bg-transparent text-ink-soft border-ink/25"
          }`}
        >
          I have a Venue
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block text-[13px] font-semibold text-ink-soft mb-1.5">
            {accountType === "venue" ? "Contact person name" : "Full name"}
          </label>
          <input
            required
            value={form.name}
            onChange={update("name")}
            className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
            placeholder={accountType === "venue" ? "e.g. Ramesh Kumar" : "e.g. Priya Sharma"}
          />
        </div>

        <div>
          <label className="block text-[13px] font-semibold text-ink-soft mb-1.5">
            {accountType === "venue" ? "Venue name" : "Stage / band name (optional)"}
          </label>
          <input
            required={accountType === "venue"}
            value={form.identityName}
            onChange={update("identityName")}
            className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
            placeholder={accountType === "venue" ? "e.g. Blue Note Lounge" : "e.g. The Midnight Echoes"}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
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
              Phone
            </label>
            <input
              type="tel"
              required
              value={form.phone}
              onChange={update("phone")}
              className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
              placeholder="+91 9xxxxxxxxx"
            />
          </div>
        </div>

        <div>
          <label className="block text-[13px] font-semibold text-ink-soft mb-1.5">
            City
          </label>
          <input
            required
            value={form.city}
            onChange={update("city")}
            className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
            placeholder="e.g. Hyderabad"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
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
          <div>
            <label className="block text-[13px] font-semibold text-ink-soft mb-1.5">
              Confirm password
            </label>
            <input
              type="password"
              required
              value={form.confirmPassword}
              onChange={update("confirmPassword")}
              className="w-full border border-ink/25 rounded-sm px-3.5 py-2.5 text-[14.5px] bg-white focus:outline-none focus:border-orange-deep"
              placeholder="••••••••"
            />
          </div>
        </div>

        {error && <p className="text-[13px] text-orange-deep">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="mt-2 bg-ink text-paper font-semibold text-[14.5px] py-3 rounded-sm disabled:opacity-60"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-[13.5px] text-ink-soft mt-6 text-center">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-orange-deep">
          Log in
        </Link>
      </p>
    </AuthLayout>
  );
}
