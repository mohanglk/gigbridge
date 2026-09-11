import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import musicianPlaceholder from "../images/musician-placeholder.svg";
import venuePlaceholder from "../images/venue-placeholder.svg";

function RatingBar({ value }) {
  const clamped = Math.max(0, Math.min(10, value));
  const pct = (clamped / 10) * 100;
  return (
    <div>
      <div className="flex items-baseline gap-2 mb-2">
        <span className="font-display text-[32px] leading-none text-ink">
          {clamped.toFixed(1)}
        </span>
        <span className="text-[14px] text-ink-soft">/ 10</span>
      </div>
      <div className="w-full h-2.5 bg-ink/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-orange-deep rounded-full"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-4 py-3.5 border-b border-ink/10 last:border-b-0">
      <span className="text-[12.5px] font-semibold tracking-wide text-ink-soft w-32 shrink-0">
        {label.toUpperCase()}
      </span>
      <span className="text-[15px] text-ink">{value || "—"}</span>
    </div>
  );
}

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const loggedIn = localStorage.getItem("gb_logged_in");
    const stored = localStorage.getItem("gb_profile");
    if (!loggedIn || !stored) {
      navigate("/login");
      return;
    }
    setProfile(JSON.parse(stored));
  }, [navigate]);

  if (!profile) return null;

  const isMusician = profile.accountType === "musician";
  const avatar = isMusician ? musicianPlaceholder : venuePlaceholder;

  return (
    <div className="min-h-screen bg-paper py-16 px-6">
      <div className="max-w-xl mx-auto">
        <div className="mb-8">
          <span className="text-[13px] font-semibold text-ink-soft">
            {isMusician ? "MUSICIAN PROFILE" : "VENUE PROFILE"}
          </span>
        </div>

        <div className="bg-white border border-ink/10 rounded-sm shadow-stamp-sm px-8 py-10">
          {/* avatar box */}
          <div className="w-32 h-32 mx-auto mb-6 rounded-sm overflow-hidden border border-ink/15 bg-paper-2">
            <img
              src={avatar}
              alt="Profile avatar"
              className="w-full h-full object-cover"
            />
          </div>

          <h2 className="font-display text-[30px] text-center leading-none mb-1">
            {profile.identityName || profile.name}
          </h2>
          {profile.identityName && (
            <p className="text-[13.5px] text-ink-soft text-center mb-6">
              {profile.name}
            </p>
          )}

          <div className="mb-8">
            <InfoRow label="Address" value={profile.address} />
            <InfoRow label="Email" value={profile.email} />
            <InfoRow label="Phone" value={profile.phone} />
            <InfoRow
              label={isMusician ? "Instrument / Role" : "Venue type"}
              value={isMusician ? profile.instrument : profile.venueType}
            />
          </div>

          <div className="pt-6 border-t border-ink/10">
            <div className="text-[12.5px] font-semibold tracking-wide text-ink-soft mb-3">
              RATING
            </div>
            <RatingBar value={profile.rating || 0} />
            <p className="text-[12.5px] text-ink-soft mt-2">
              {profile.ratingCount
                ? `Based on ${profile.ratingCount} reviews`
                : "No reviews yet — this score updates after your first gig."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
