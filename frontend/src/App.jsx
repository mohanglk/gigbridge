import { Routes, Route, Link, useLocation } from "react-router-dom";
import Landing from "./pages/Landing";
import Home from "./pages/Home";
import Waitlist from "./pages/Waitlist";
import Login from "./pages/Login";
import Register from "./pages/Register";

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
      <div className="flex items-center gap-5">
        <Link to="/login" className="text-sm font-semibold text-ink">
          Log in
        </Link>
        <Link
          to="/waitlist"
          className="text-sm font-semibold bg-ink text-paper px-4.5 py-2 rounded-sm"
        >
          Join the waitlist
        </Link>
      </div>
    </nav>
  );
}

const NO_NAV_ROUTES = ["/waitlist", "/login", "/register"];

export default function App() {
  const location = useLocation();
  const hideNav = NO_NAV_ROUTES.includes(location.pathname);

  return (
    <div className="min-h-screen bg-paper">
      {!hideNav && <Nav />}
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/status" element={<Home />} />
        <Route path="/waitlist" element={<Waitlist />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </div>
  );
}
