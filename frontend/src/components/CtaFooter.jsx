export default function CtaFooter() {
  return (
    <footer id="join" className="bg-ink text-paper pt-24 pb-10">
      <div className="max-w-[1160px] mx-auto px-8">
        <div className="text-center max-w-xl mx-auto mb-16">
          <h3 className="font-display text-[36px] md:text-[54px] leading-[0.95] mb-5">
            Ready to bridge
            <br />
            the gig gap?
          </h3>
          <p className="text-[16px] opacity-80 mb-8">
            We&apos;re building the Phase 1 MVP now — 10 real bands, 3 club
            venues, one city.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href="#"
              className="text-[14.5px] font-bold px-6 py-3 rounded-sm bg-orange text-ink"
            >
              I&apos;m a musician
            </a>
            <a
              href="#"
              className="text-[14.5px] font-bold px-6 py-3 rounded-sm bg-transparent border-[1.5px] border-paper text-paper"
            >
              I&apos;m a venue
            </a>
          </div>
        </div>
        <div className="flex justify-between items-center flex-wrap gap-3 pt-8 border-t border-paper/20 text-[13px] opacity-65">
          <div>GIGBRIDGE — a professional network &amp; gig-booking platform</div>
          <div>Concept · Tech Stack · Architecture · Roadmap</div>
        </div>
      </div>
    </footer>
  );
}
