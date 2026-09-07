const steps = [
  {
    num: "01",
    title: "Sign up",
    body: "Register as musician or venue with email or social login.",
    venue: false,
  },
  {
    num: "02",
    title: "Build your profile",
    body: "Add instruments, genres, experience, demo audio and video.",
    venue: false,
  },
  {
    num: "03",
    title: "Create or join a band",
    body: "Set up a band page, or browse vacancies and send join requests.",
    venue: false,
  },
  {
    num: "04",
    title: "Get discovered",
    body: "Your profile and band become searchable by venues and artists.",
    venue: false,
  },
  {
    num: "05",
    title: "Receive booking requests",
    body: "Accept, negotiate or decline gig offers from venues.",
    venue: true,
  },
  {
    num: "06",
    title: "Perform the gig",
    body: "Calendar synced; gig details and payout tracked in-app.",
    venue: true,
  },
  {
    num: "07",
    title: "Earn reviews",
    body: "Ratings raise your trust score, which brings more bookings.",
    venue: true,
  },
];

export default function WorkflowSection() {
  return (
    <section className="py-24 bg-paper-2">
      <div className="max-w-[1160px] mx-auto px-8">
        <div className="max-w-xl mb-14">
          <div className="text-[13px] font-semibold text-orange-deep mb-2">
            WORKFLOW
          </div>
          <h3 className="font-display text-[34px] md:text-[46px] leading-none">
            The musician journey,
            <br />
            start to payout.
          </h3>
        </div>
        <div className="border-t-[1.5px] border-ink">
          {steps.map((s, i) => (
            <div
              key={i}
              className="grid grid-cols-[70px_1fr] border-b-[1.5px] border-ink py-5"
            >
              <div
                className={`font-display text-[34px] ${
                  s.venue ? "text-teal-deep" : "text-orange-deep"
                }`}
              >
                {s.num}
              </div>
              <div>
                <h5 className="text-[16px] font-bold mb-1">{s.title}</h5>
                <p className="text-[14px] text-ink-soft">{s.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
