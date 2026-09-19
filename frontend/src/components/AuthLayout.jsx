import { Link } from "react-router-dom";

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen bg-ink flex flex-col items-center justify-center px-6 py-16">
      <Link
        to="/"
        className="font-display text-[26px] tracking-wide text-paper mb-10"
      >
        GIG<span className="text-orange">BRIDGE</span>
      </Link>

      <div className="w-full max-w-md bg-paper rounded-sm shadow-stamp px-8 py-10">
        <h2 className="font-display text-[30px] leading-none mb-2 text-ink">
          {title}
        </h2>
        {subtitle && (
          <p className="text-[14px] text-ink-soft mb-8">{subtitle}</p>
        )}
        {children}
      </div>
    </div>
  );
}
