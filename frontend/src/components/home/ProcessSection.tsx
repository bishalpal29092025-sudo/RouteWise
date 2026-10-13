
import { motion } from "motion/react";

const processSteps = [
  {
    number: "01",
    title: "Enter your journey",
    description:
      "Choose your US origin, destination, departure time, and truck load.",
  },
  {
    number: "02",
    title: "Evaluate conditions",
    description:
      "Check weather forecasts at estimated arrival times along the route.",
  },
  {
    number: "03",
    title: "Compare route risks",
    description:
      "Review risk classifications and the available route recommendation.",
  },
];

export default function ProcessSection() {
  return (
    <section className="process-section section-wrap" id="process">
      <div className="process-heading">
        <span className="section-kicker">HOW IT WORKS</span>
        <h2>From departure to decision.</h2>
      </div>

      <div className="process-grid">
        {processSteps.map((step, index) => (
          <motion.div
            className="process-step"
            key={step.number}
            initial={{ opacity: 0, x: index % 2 === 0 ? -15 : 15 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5, delay: index * 0.12 }}
          >
            <span className="process-number">{step.number}</span>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
