const musicianProblems = [
  "Scattered across Instagram, YouTube and WhatsApp — no professional identity",
  "Hard to find bandmates, or bands with open vacancies",
  "Experience and past gigs are never visible in one verified place",
  "Gigs come only through word of mouth",
];

const venueProblems = [
  "No searchable, verified pool of performing bands nearby",
  "Booking happens over calls and brokers — slow, opaque pricing",
  "No way to judge reliability or genre fit before booking",
  "Last-minute cancellations, no backup discovery channel",
];

function ProblemColumn({ title, items, accent }) {
  return (
    <div className="px-8 py-10 md:px-10">
      <h4 className={`font-display text-[26px] mb-4 ${accent}`}>{title}</h4>
      <ul>
        {items.map((item, i) => (
          <li
            key={i}
            className={`text-[14.5px] pl-5 py-3 relative ${
              i !== 0 ? "border-t border-ink/15" : ""
            }`}
          >
            <span className="absolute left-0 text-ink-soft">—</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ProblemSection() {
  return (
    <section id="problem" className="py-24">
      <div className="max-w-[1160px] mx-auto px-8">
        <div className="max-w-xl mb-14">
          <div className="text-[13px] font-semibold text-orange-deep mb-2">
            THE PROBLEM
          </div>
          <h3 className="font-display text-[34px] md:text-[46px] leading-none">
            Talent and stages can&apos;t
            <br />
            find each other.
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 border-[1.5px] border-ink">
          <div className="border-b-[1.5px] md:border-b-0 md:border-r-[1.5px] border-ink">
            <ProblemColumn
              title="Independent Musicians"
              items={musicianProblems}
              accent="text-orange-deep"
            />
          </div>
          <ProblemColumn
            title="Clubs & Venues"
            items={venueProblems}
            accent="text-teal-deep"
          />
        </div>
      </div>
    </section>
  );
}
