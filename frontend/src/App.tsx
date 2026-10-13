
import { useEffect, useState, type FormEvent } from "react";

import { checkBackendHealth, planRoute } from "./lib/api";
import type { RoutePlanResponse } from "./lib/api";

import "./App.css";

import Navbar from "./components/layout/Navbar";
import HeroSection from "./components/home/HeroSection";
import MetricsStrip from "./components/home/MetricsStrip";
import FeaturesSection from "./components/home/FeaturesSection";
import ProcessSection from "./components/home/ProcessSection";
import RoutePlannerForm from "./components/planner/RoutePlannerForm";
import Footer from "./components/layout/Footer";

type Theme = "light" | "dark";

type BackendStatus = "checking" | "connected" | "error";

const riskCategories = ["Low", "Moderate", "High", "Severe", "No Travel"];

function getLocalDateTime(): string {
  const date = new Date();
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());

  return date.toISOString().slice(0, 16);
}

function formatNumber(
  value: number,
  maximumFractionDigits = 1,
): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits,
  }).format(value);
}

function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours === 0) return `${minutes} min`;
  if (minutes === 0) return `${hours} hr`;

  return `${hours} hr ${minutes} min`;
}

function formatArrival(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return `${date.toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  })} UTC`;
}

function getRiskClass(value: string): string {
  return value.toLowerCase().replace(/\s+/g, "-");
}

function getSafetyMessage(result: RoutePlanResponse): string {
  if (result.safety_status === "no_safe_route_available") {
    return "No available route satisfies the current safety rules. Do not treat any route as safe.";
  }

  if (result.safety_status === "safe_route_available") {
    return "The risk algorithm found a route without No Travel checkpoints. This is not a guarantee of real-world truck safety.";
  }

  return "Review the route results and weather risks before making a travel decision.";
}

function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      return localStorage.getItem("routewise-theme") === "light"
        ? "light"
        : "dark";
    } catch {
      return "dark";
    }
  });

  const [menuOpen, setMenuOpen] = useState(false);

  const [backendStatus, setBackendStatus] =
    useState<BackendStatus>("checking");

  const [origin, setOrigin] = useState("New York, NY, USA");

  const [destination, setDestination] = useState("Chicago, IL, USA");

  const [departureTime, setDepartureTime] =
    useState(getLocalDateTime);

  const [truckLoad, setTruckLoad] = useState("25000");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [result, setResult] = useState<RoutePlanResponse | null>(null);

  // Check whether the Django backend is reachable.
  useEffect(() => {
    let cancelled = false;

    checkBackendHealth()
      .then(() => {
        if (!cancelled) {
          setBackendStatus("connected");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setBackendStatus("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Apply and remember the selected theme.
  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      theme === "dark",
    );

    document.documentElement.dataset.theme = theme;

    try {
      localStorage.setItem("routewise-theme", theme);
    } catch {
      // The application still works if browser storage is unavailable.
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((current) =>
      current === "dark" ? "light" : "dark",
    );
  };

  const closeMenu = () => {
    setMenuOpen(false);
  };

  const scrollToPlanner = () => {
    document.getElementById("planner")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

    closeMenu();
  };

  // Validate the form and request a route from the backend.
  async function handlePlanRoute(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");
    setResult(null);

    if (
      origin.trim().toLowerCase() ===
      destination.trim().toLowerCase()
    ) {
      setError("Origin and destination must be different.");
      return;
    }

    const departure = new Date(departureTime);

    if (Number.isNaN(departure.getTime())) {
      setError("Please enter a valid departure date and time.");
      return;
    }

    if (departure.getTime() < Date.now()) {
      setError("Please choose a departure time in the future.");
      return;
    }

    const load = Number(truckLoad);

    if (!Number.isFinite(load) || load <= 0) {
      setError("Truck load must be a number greater than zero.");
      return;
    }

    setLoading(true);

    try {
      const response = await planRoute({
        origin: origin.trim(),
        destination: destination.trim(),
        departure_time: departure.toISOString(),
        truck_load_lbs: truckLoad,
      });

      setResult(response);

      window.setTimeout(() => {
        document.getElementById("route-results")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to calculate the route. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  const recommendedRoute = result?.routes.find(
    (route) => route.route_id === result.recommended_route_id,
  );

  return (
    <div className="app-shell">
      <Navbar
        theme={theme}
        backendStatus={backendStatus}
        menuOpen={menuOpen}
        toggleTheme={toggleTheme}
        closeMenu={closeMenu}
        scrollToPlanner={scrollToPlanner}
        setMenuOpen={setMenuOpen}
      />

      <main>
        <HeroSection
          backendStatus={backendStatus}
          scrollToPlanner={scrollToPlanner}
        />

        <MetricsStrip />

        <FeaturesSection />

        <RoutePlannerForm
          backendStatus={backendStatus}
          origin={origin}
          setOrigin={setOrigin}
          destination={destination}
          setDestination={setDestination}
          departureTime={departureTime}
          setDepartureTime={setDepartureTime}
          truckLoad={truckLoad}
          setTruckLoad={setTruckLoad}
          loading={loading}
          error={error}
          result={result}
          handlePlanRoute={handlePlanRoute}
          getLocalDateTime={getLocalDateTime}
          recommendedRoute={recommendedRoute}
          getSafetyMessage={getSafetyMessage}
          formatNumber={formatNumber}
          formatDuration={formatDuration}
          formatArrival={formatArrival}
          getRiskClass={getRiskClass}
          riskCategories={riskCategories}
        />

        <ProcessSection />
      </main>

      <Footer />
    </div>
  );
}

export default App;
