
import {
  CloudSun,
  Compass,
  Gauge,
  ShieldCheck,
} from "lucide-react";

export default function MetricsStrip() {
  return (
    <section
      className="metrics-strip"
      aria-label="Platform capabilities"
    >
      <div className="metric-item">
        <span className="metric-icon">
          <Compass size={19} />
        </span>
        <span>
          <strong>Route alternatives</strong>
          <small>Available road paths</small>
        </span>
      </div>

      <div className="metric-item">
        <span className="metric-icon">
          <CloudSun size={19} />
        </span>
        <span>
          <strong>Weather checkpoints</strong>
          <small>Forecast along the journey</small>
        </span>
      </div>

      <div className="metric-item">
        <span className="metric-icon">
          <ShieldCheck size={19} />
        </span>
        <span>
          <strong>Safety-first ranking</strong>
          <small>Risk before travel time</small>
        </span>
      </div>

      <div className="metric-item">
        <span className="metric-icon">
          <Gauge size={19} />
        </span>
        <span>
          <strong>Load-aware analysis</strong>
          <small>Consider truck weight</small>
        </span>
      </div>
    </section>
  );
}