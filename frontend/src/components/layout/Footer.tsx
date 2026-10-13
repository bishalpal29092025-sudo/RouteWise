
import { Command, Compass } from "lucide-react";

export default function Footer() {
  return (
    <footer className="site-footer">
      <a className="brand footer-brand" href="#home">
        <span className="brand-mark">
          <Compass size={19} />
        </span>
        <span className="brand-copy">
          <strong>RouteWise</strong>
          <span>WEATHER INTELLIGENCE</span>
        </span>
      </a>

      <span className="footer-disclaimer">
        Weather-aware planning support. Always follow official safety
        guidance.
      </span>

      <span className="footer-copyright">
        <Command size={13} /> RouteWise · Project preview
      </span>
    </footer>
  );
}
