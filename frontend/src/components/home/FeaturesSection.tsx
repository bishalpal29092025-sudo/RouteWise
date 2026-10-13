
import { motion } from "motion/react";
import {
  ArrowRight,
  CloudSun,
  MapPinned,
  ShieldCheck,
} from "lucide-react";

const features = [
  {
    icon: MapPinned,
    title: "Intelligent routing",
    description:
      "Compare the road routes returned by our routing provider, including distance and estimated travel time.",
    color: "cyan",
  },
  {
    icon: CloudSun,
    title: "Weather intelligence",
    description:
      "Evaluate wind, rain, and snow at route checkpoints using available forecast data.",
    color: "violet",
  },
  {
    icon: ShieldCheck,
    title: "Safety-first decisions",
    description:
      "Prioritize severe risk, high risk, average risk, and travel time when comparing routes.",
    color: "emerald",
  },
];

export default function FeaturesSection() {
  return (
    <section className="features-section section-wrap" id="features">
      <motion.div
        className="section-heading"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.35 }}
        transition={{ duration: 0.6 }}
      >
        <span className="section-kicker">BUILTFOR THE JOURNEY</span>
        <h2>
          Every decision starts
          <br />
          with <span className="gradient-text">better information.</span>
        </h2>
        <p>
          Review available road routes, weather conditions, and safety
          considerations in one place.
        </p>
      </motion.div>

      <div className="feature-grid">
        {features.map((feature, index) => {
          const Icon = feature.icon;

          return (
            <motion.article
              className="feature-card"
              key={feature.title}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.5, delay: index * 0.12 }}
              whileHover={{ y: -6 }}
            >
              <div className={`feature-icon ${feature.color}`}>
                <Icon size={23} />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <span className="feature-arrow" aria-hidden="true">
                <ArrowRight size={17} />
              </span>
            </motion.article>
          );
        })}
      </div>
    </section>
  );
}
