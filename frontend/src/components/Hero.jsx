export default function Hero() {
  return (
    <section className="relative grid grid-cols-1 md:grid-cols-2 min-h-[560px] overflow-hidden border-y border-ink/20">
      <div className="relative flex flex-col justify-center px-7 py-16 md:px-14 bg-orange-deep text-paper">
        <div className="text-[13px] font-semibold tracking-wide opacity-85 mb-3">
          FOR MUSICIANS &amp; BANDS
        </div>
        <h2 className="font-display text-[40px] md:text-[58px] leading-[0.95] mb-4">
          STOP CHASING
          <br />
          GIGS THROUGH
          <br />
          DMS.
        </h2>
        <p className="max-w-xs text-[15.5px] opacity-90 mb-6">
          One verified profile for your instruments, genres and demo tracks —
          venues find you, not the other way round.
        </p>
        <a
          href="#"
          className="inline-block w-fit text-sm font-semibold bg-paper text-ink px-5 py-2.5 rounded-sm"
        >
          Create your profile
        </a>
      </div>

      {/* torn seam divider, desktop only */}
      <div className="hidden md:block torn-seam absolute top-0 bottom-0 left-1/2 w-9 -ml-[18px] bg-paper z-20" />

      {/* center wordmark stamp */}
      <div className="static md:absolute md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 z-30 text-center bg-paper border-2 border-ink px-7 py-4 shadow-stamp-sm md:shadow-stamp mx-auto my-6 md:my-0 w-fit">
        <div className="font-display text-[44px] text-ink leading-none">
          GIGBRIDGE
        </div>
        <small className="block text-[11.5px] font-semibold tracking-wide text-ink-soft mt-1">
          MUSICIANS ⟷ VENUES
        </small>
      </div>

      <div className="relative flex flex-col justify-center px-7 py-16 md:px-14 bg-teal-deep text-paper">
        <div className="text-[13px] font-semibold tracking-wide opacity-85 mb-3">
          FOR CLUBS &amp; VENUES
        </div>
        <h2 className="font-display text-[40px] md:text-[58px] leading-[0.95] mb-4">
          STOP BOOKING
          <br />
          BANDS ON
          <br />
          WORD OF MOUTH.
        </h2>
        <p className="max-w-xs text-[15.5px] opacity-90 mb-6">
          Search bands by city, genre, size and budget. See ratings and demo
          media before you send an offer.
        </p>
        <a
          href="#"
          className="inline-block w-fit text-sm font-semibold bg-paper text-ink px-5 py-2.5 rounded-sm"
        >
          Find your lineup
        </a>
      </div>
    </section>
  );
}
