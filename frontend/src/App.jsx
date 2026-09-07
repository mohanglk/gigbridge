import { Routes, Route, Link, useLocation } from "react-router-dom";
import Landing from "./pages/Landing";
import Home from "./pages/Home";
import Waitlist from "./pages/Waitlist";

function Nav() {
  return (
    <nav className="flex items-center justify-between px-8 py-6 max-w-[1160px] mx-auto">
      <Link to="/" className="font-display text-[26px] tracking-wide">
        GIG<span className="text-orange-deep">BRIDGE</span>
      </Link>
      <div className="hidden md:flex gap-9 text-sm font-medium">
        <a href="#problem" className="border-b border-transparent hover:border-ink pb-0.5">
          Why
        </a>
        <a href="#solution" className="border-b border-transparent hover:border-ink pb-0.5">
          How it works
        </a>
        <a href="#features" className="border-b border-transparent hover:border-ink pb-0.5">
          Features
        </a>
        <a href="#stack" className="border-b border-transparent hover:border-ink pb-0.5">
          Built on
        </a>
      </div>
      <Link
        to="/waitlist"
        className="text-sm font-semibold bg-ink text-paper px-4.5 py-2 rounded-sm"
      >
        Join the waitlist
      </Link>
    </nav>
  );
}

export default function App() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-paper">
      {location.pathname !== "/waitlist" && <Nav />}
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/status" element={<Home />} />
        <Route path="/waitlist" element={<Waitlist />} />
      </Routes>
    </div>
  );
}
