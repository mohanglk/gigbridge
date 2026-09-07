const stack = [
  { tag: "FRONTEND", val: "React + Tailwind" },
  { tag: "BACKEND", val: "Python FastAPI" },
  { tag: "DATABASE", val: "PostgreSQL + Redis" },
  { tag: "MEDIA", val: "AWS S3 + CloudFront" },
  { tag: "AUTH & PAY", val: "JWT/OAuth2 + Razorpay" },
  { tag: "DEVOPS", val: "Docker + AWS ECS" },
];

export default function StackSection() {
  return (
    <section id="stack" className="py-24">
      <div className="max-w-[1160px] mx-auto px-8">
        <div className="max-w-xl mb-14">
          <div className="text-[13px] font-semibold text-orange-deep mb-2">
            BUILT ON
          </div>
          <h3 className="font-display text-[34px] md:text-[46px] leading-none mb-4">
            A stack you already
            <br />
            ship in production.
          </h3>
          <p className="text-[16px] text-ink-soft max-w-md">
            React on the front end, FastAPI on the back — the same
            architecture from the pitch deck, ready for the Phase 1 MVP.
          </p>
        </div>
        <div className="flex flex-wrap gap-px bg-ink border border-ink">
          {stack.map((s, i) => (
            <div key={i} className="flex-1 min-w-[150px] bg-paper px-5 py-5">
              <div className="text-[11.5px] font-bold text-ink-soft mb-1.5">
                {s.tag}
              </div>
              <div className="text-[15px] font-bold">{s.val}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
