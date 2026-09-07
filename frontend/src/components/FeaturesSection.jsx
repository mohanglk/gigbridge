const musicianFeatures = [
  {
    title: "Profile & Portfolio",
    body: "Bio, instruments, genres, years of experience — plus demo tracks, videos and gig photos.",
  },
  {
    title: "Band Pages",
    body: "Member roster, band size, genre, formation year and combined experience.",
  },
  {
    title: "Vacancies & Join Requests",
    body: "Bands post open roles; solo artists apply to join in one tap.",
  },
  {
    title: "Network & Messaging",
    body: "Follow artists, endorse skills, chat to plan jams and auditions.",
  },
];

const venueFeatures = [
  {
    title: "Smart Band Search",
    body: "Filter by city, genre, size and price; preview demo media before shortlisting.",
  },
  {
    title: "Booking Engine",
    body: "Send a request, track status — pending, negotiating, confirmed.",
  },
  {
    title: "Event Calendar",
    body: "One calendar of upcoming gigs with reminders and backup workflows.",
  },
  {
    title: "Ratings & Reviews",
    body: "Two-way reviews build a trust score for both bands and venues.",
  },
];

function FeatureGrid({ label, items }) {
  return (
    <div className="mb-16 last:mb-0">
      <div className="font-display text-[20px] mb-5 pb-2.5 border-b-2 border-ink inline-block">
        {label}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-px bg-ink border border-ink">
        {items.map((f, i) => (
          <div key={i} className="bg-paper px-6 py-6">
            <h5 className="text-[15px] font-bold mb-2">{f.title}</h5>
            <p className="text-[13.5px] text-ink-soft leading-relaxed">
              {f.body}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function FeaturesSection() {
  return (
    <section id="features" className="py-24">
      <div className="max-w-[1160px] mx-auto px-8">
        <div className="max-w-xl mb-14">
          <div className="text-[13px] font-semibold text-orange-deep mb-2">
            KEY FEATURES
          </div>
          <h3 className="font-display text-[34px] md:text-[46px] leading-none">
            Everything both sides
            <br />
            actually need.
          </h3>
        </div>
        <FeatureGrid label="For musicians & bands" items={musicianFeatures} />
        <FeatureGrid label="For clubs & venues" items={venueFeatures} />
      </div>
    </section>
  );
}
