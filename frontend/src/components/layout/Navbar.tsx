
import type { Dispatch, SetStateAction } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  ArrowRight,
  Compass,
  Menu,
  Moon,
  Sun,
  X,
} from "lucide-react";

type Theme = "light" | "dark";
type BackendStatus = "checking" | "connected" | "error";

interface NavbarProps {
  theme: Theme;
  backendStatus: BackendStatus;
  menuOpen: boolean;
  toggleTheme: () => void;
  closeMenu: () => void;
  scrollToPlanner: () => void;
  setMenuOpen: Dispatch<SetStateAction<boolean>>;
}

export default function Navbar({
  theme,
  backendStatus,
  menuOpen,
  toggleTheme,
  closeMenu,
  scrollToPlanner,
  setMenuOpen,
}: NavbarProps) {
  return (
    <header className="topbar">
      <a
        className="brand"
        href="#home"
        aria-label="RouteWise home"
        onClick={closeMenu}
      >
        <span className="brand-mark">
          <Compass size={22} strokeWidth={2.3} />
        </span>

        <span className="brand-copy">
          <strong>RouteWise</strong>
          <span>WEATHER INTELLIGENCE</span>
        </span>
      </a>

      <nav
        className={`nav-links ${menuOpen ? "nav-open" : ""}`}
        aria-label="Main navigation"
      >
        <a href="#features" onClick={closeMenu}>
          Features
        </a>

        <a href="#process" onClick={closeMenu}>
          How it works
        </a>

        <button className="mobile-plan-link" onClick={scrollToPlanner}>
          Plan a route <ArrowRight size={16} />
        </button>
      </nav>

      <div className="nav-actions">
        <span
          className="system-status"
          role="status"
          aria-live="polite"
          title={`Django backend: ${backendStatus}`}
        >
          <span
            className="status-dot"
            style={{
              backgroundColor:
                backendStatus === "connected"
                  ? "#22c55e"
                  : backendStatus === "error"
                    ? "#ef4444"
                    : "#f59e0b",
            }}
          />

          {backendStatus === "connected"
            ? "BACKEND CONNECTED"
            : backendStatus === "error"
              ? "BACKEND OFFLINE"
              : "CONNECTING…"}
        </span>

        <button
          className="icon-button theme-button"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.span
              key={theme}
              className="icon-motion"
              initial={{ opacity: 0, rotate: -45, scale: 0.7 }}
              animate={{ opacity: 1, rotate: 0, scale: 1 }}
              exit={{ opacity: 0, rotate: 45, scale: 0.7 }}
              transition={{ duration: 0.18 }}
            >
              {theme === "dark" ? <Sun size={19} /> : <Moon size={19} />}
            </motion.span>
          </AnimatePresence>
        </button>

        <button className="nav-cta" onClick={scrollToPlanner}>
          Plan a route <ArrowRight size={16} />
        </button>

        <button
          className="icon-button menu-button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
        >
          {menuOpen ? <X size={21} /> : <Menu size={21} />}
        </button>
      </div>
    </header>
  );
}
