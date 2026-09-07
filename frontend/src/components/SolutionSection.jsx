function Stub({ num, title, items, dotClass }) {
  return (
    <div className="bg-paper-2 border-[1.5px] border-dashed border-ink-soft rounded-md px-8 pt-8 pb-7">
      <div className="font-display text-[13px] tracking-wide text-ink-soft mb-2">
        {num}
      </div>
      <h4 className="font-display text-[28px] mb-3">{title}</h4>
      <ul>
        {items.map((item, i) => (
          <li key={i} className="text-[14.5px] pl-4 py-1.5 relative">
            <span className={`absolute left-0 ${dotClass}`}>•</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function SolutionSection() {
  return (
    <section id="solution" className="py-24 bg-paper-2">
      <div className="max-w-[1160px] mx-auto px-8">
        <div className="max-w-xl mb-14">
          <div className="text-[13px] font-semibold text-orange-deep mb-2">
            THE SOLUTION
          </div>
          <h3 className="font-display text-[34px] md:text-[46px] leading-none">
            One platform, two
            <br />
            core objectives.
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-7">
          <Stub
            num="OBJECTIVE 01"
            title="Profiles & Networking"
            dotClass="text-orange-deep"
            items={[
              "Rich profiles — instruments, genres, demo audio/video",
              "Band pages with size, members, genre & experience",
              '"Looking to join" / "Vacancy open" matching',
              "Follow, endorse and message other artists",
            ]}
          />
          <Stub
            num="OBJECTIVE 02"
            title="Discovery & Booking"
            dotClass="text-teal-deep"
            items={[
              "Search bands by city, genre, size and budget",
              "Send requests with date, time slot and offer",
              "Accept, negotiate or decline — calendar stays synced",
              "Post-gig ratings build trust on both sides",
            ]}
          />
        </div>
      </div>
    </section>
  );
}
