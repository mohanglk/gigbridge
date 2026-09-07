import Hero from "../components/Hero";
import ProblemSection from "../components/ProblemSection";
import SolutionSection from "../components/SolutionSection";
import FeaturesSection from "../components/FeaturesSection";
import WorkflowSection from "../components/WorkflowSection";
import CtaFooter from "../components/CtaFooter";

export default function Landing() {
  return (
    <div className="bg-paper text-ink font-body paper-texture">
      <Hero />
      <ProblemSection />
      <SolutionSection />
      <FeaturesSection />
      <WorkflowSection />
      <CtaFooter />
    </div>
  );
}
