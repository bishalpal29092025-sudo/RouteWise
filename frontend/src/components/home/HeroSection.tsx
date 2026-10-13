
import { motion } from "motion/react";
import {
  Activity,
  ArrowDown,
  ArrowRight,
  Layers3,
  ShieldCheck,
  Wind,
} from "lucide-react";

interface HeroSectionProps {
  backendStatus: "checking" | "connected" | "error";
  scrollToPlanner: () => void;
}

export default function HeroSection({
  backendStatus,
  scrollToPlanner,
}: HeroSectionProps) {
  return (
    <section className="hero-section" id="home">
      <div className="hero-glow hero-glow-one" aria-hidden="true" />
      <div className="hero-glow hero-glow-two" aria-hidden="true" />

      <div className="hero-content">
        <motion.div
          className="eyebrow"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
        >
          <span className="eyebrow-icon">
            <Activity size={14} />
          </span>
          SMARTER ROUTES. SAFER JOURNEYS.
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.08 }}
        >
          The road ahead,
          <br />
          <span className="gradient-text">under every forecast.</span>
        </motion.h1>

        <motion.p
          className="hero-description"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.2 }}
        >
          Plan truck journeys across the United States. Compare available
          road routes, understand changing weather risks, and put safety
          first.
        </motion.p>

        <motion.div
          className="hero-actions"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.3 }}
        >
          <button className="primary-button" onClick={scrollToPlanner}>
            Plan your journey <ArrowRight size={18} />
          </button>

          <a className="secondary-button" href="#features">
            Explore features <ArrowDown size={17} />
          </a>
        </motion.div>

        <motion.div
          className="hero-note"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.65, duration: 0.6 }}
        >
          <span className="note-check">
            <ShieldCheck size={16} />
          </span>
          Weather-aware planning support for better-informed decisions
        </motion.div>
      </div>

      <motion.div
        className="hero-visual"
        initial={{ opacity: 0, scale: 0.92, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.85, delay: 0.25 }}
      >
        <div className="visual-topline">
          <div className="visual-label">
            <span className="visual-label-icon">
              <Layers3 size={15} />
            </span>
            ROUTE OVERVIEW
          </div>

          <span className="live-indicator">
            <span className="status-dot" /> INTERFACE PREVIEW
          </span>
        </div>

        <div className="route-art">
          <div className="map-grid" aria-hidden="true" />

          <svg
            className="route-svg"
            viewBox="0 0 500 330"
            role="img"
            aria-label="Illustration of possible routes; actual routes are shown in the planner results."
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <linearGradient
                id="routePrimary"
                x1="0"
                y1="0"
                x2="1"
                y2="1"
              >
                <stop offset="0%" stopColor="#22d3ee" />
                <stop offset="100%" stopColor="#818cf8" />
              </linearGradient>

              <filter
                id="routeGlow"
                x="-30%"
                y="-30%"
                width="160%"
                height="160%"
              >
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            <g className="map-roads">
              <path d="M 15 50 L 140 100 L 225 60 L 335 110 L 480 40" />
              <path d="M 10 220 L 110 190 L 190 250 L 290 210 L 485 280" />
              <path d="M 70 0 L 120 90 L 100 165 L 170 330" />
              <path d="M 380 0 L 345 85 L 395 165 L 355 330" />
              <path d="M 0 140 L 160 150 L 270 135 L 500 170" />
              <path d="M 230 0 L 250 80 L 225 165 L 270 330" />
            </g>

            <g className="route-secondary">
              <path d="M 60 285 Q 145 235 210 190 T 440 40" />
              <path d="M 60 285 Q 160 305 260 245 T 440 40" />
            </g>

            <motion.path
              className="route-primary"
              d="M 60 285 C 105 245 125 225 180 210 S 265 120 320 140 S 400 105 440 40"
              pathLength={1}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{
                duration: 2,
                delay: 0.6,
                ease: "easeInOut",
              }}
              filter="url(#routeGlow)"
            />

            <g className="map-point origin-point">
              <circle cx="60" cy="285" r="12" />
              <circle cx="60" cy="285" r="5" />
            </g>

            <g className="map-point destination-point">
              <circle cx="440" cy="40" r="12" />
              <circle cx="440" cy="40" r="5" />
            </g>

            <g className="weather-point">
              <circle cx="180" cy="210" r="14" />
              <path d="M 180 201 L 180 219 M 171 210 L 189 210" />
            </g>

            <g className="weather-point">
              <circle cx="320" cy="140" r="14" />
              <path d="M 320 131 L 320 149 M 311 140 L 329 140" />
            </g>
          </svg>

          <motion.div
            className="map-label label-origin"
            animate={{ y: [0, -3, 0] }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <span className="label-dot" />
            ORIGIN
          </motion.div>

          <motion.div
            className="map-label label-destination"
            animate={{ y: [0, 3, 0] }}
            transition={{
              duration: 3.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <span className="label-dot" />
            DESTINATION
          </motion.div>

          <div className="map-caption">
            <Wind size={16} />
            Real route and checkpoint details appear in your plan results.
          </div>
        </div>

        <div className="visual-footer">
          <div>
            <span className="footer-kicker">PLATFORM STATUS</span>

            <strong>
              {backendStatus === "connected"
                ? "Backend connected"
                : backendStatus === "error"
                  ? "Backend unavailable"
                  : "Checking connection"}
            </strong>
          </div>

          <span className="preview-badge">PREVIEW</span>
        </div>
      </motion.div>
    </section>
  );
}
