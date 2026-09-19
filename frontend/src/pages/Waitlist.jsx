import { useNavigate } from "react-router-dom";

function MusicianIcon() {
  return (
    <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* head */}
      <circle cx="40" cy="18" r="10" fill="#4b5563" />
      {/* body */}
      <path d="M24 60 Q24 42 40 42 Q56 42 56 60" fill="#4b5563" />
      {/* microphone stand */}
      <rect x="38" y="52" width="4" height="16" rx="2" fill="#374151" />
      <rect x="32" y="66" width="16" height="3" rx="1.5" fill="#374151" />
      {/* microphone */}
      <rect x="35" y="38" width="10" height="16" rx="5" fill="#374151" />
      {/* mic grille lines */}
      <line x1="35" y1="44" x2="45" y2="44" stroke="#6b7280" strokeWidth="1.2" />
      <line x1="35" y1="48" x2="45" y2="48" stroke="#6b7280" strokeWidth="1.2" />
      {/* arm holding mic */}
      <path d="M40 42 Q50 46 43 52" stroke="#4b5563" strokeWidth="4" strokeLinecap="round" fill="none" />
    </svg>
  );
}

function VenueIcon() {
  return (
    <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* building body */}
      <rect x="10" y="30" width="60" height="42" rx="2" fill="#4b5563" />
      {/* roof / triangle */}
      <path d="M6 32 L40 10 L74 32Z" fill="#374151" />
      {/* door */}
      <rect x="33" y="52" width="14" height="20" rx="2" fill="#1f2937" />
      {/* door knob */}
      <circle cx="44" cy="63" r="1.5" fill="#6b7280" />
      {/* windows */}
      <rect x="14" y="38" width="12" height="10" rx="1" fill="#1f2937" />
      <rect x="54" y="38" width="12" height="10" rx="1" fill="#1f2937" />
      {/* stage lights on roof */}
      <circle cx="28" cy="30" r="3" fill="#6b7280" />
      <circle cx="40" cy="26" r="3" fill="#6b7280" />
      <circle cx="52" cy="30" r="3" fill="#6b7280" />
      {/* sign board */}
      <rect x="22" y="34" width="36" height="10" rx="1" fill="#1f2937" />
      <line x1="28" y1="39" x2="52" y2="39" stroke="#6b7280" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export default function Waitlist() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-ink flex flex-col items-center justify-center px-6">
      <h2 className="font-display text-[36px] md:text-[52px] text-paper mb-12 tracking-wide">
        JOIN THE WAITLIST
      </h2>

      <div className="flex flex-col sm:flex-row gap-8">
        {/* Musician box */}
        <button
          onClick={() => navigate("/register?type=musician")}
          className="bg-[#e5e7eb] text-ink w-64 h-64 flex flex-col items-center justify-center gap-4 rounded-sm shadow-stamp hover:scale-105 transition-transform cursor-pointer"
        >
          <MusicianIcon />
          <span className="font-display text-[28px] tracking-wide">MUSICIAN</span>
          <span className="text-[13px] text-ink-soft font-medium">I perform &amp; play</span>
        </button>

        {/* Venue box */}
        <button
          onClick={() => navigate("/register?type=venue")}
          className="bg-[#e5e7eb] text-ink w-64 h-64 flex flex-col items-center justify-center gap-4 rounded-sm shadow-stamp hover:scale-105 transition-transform cursor-pointer"
        >
          <VenueIcon />
          <span className="font-display text-[28px] tracking-wide">VENUE</span>
          <span className="text-[13px] text-ink-soft font-medium">I book &amp; host gigs</span>
        </button>
      </div>

      <p className="text-paper/50 text-[13px] mt-10">
        Choose what best describes you to get started
      </p>
    </div>
  );
}
