
import { motion } from "motion/react";
import {
  ArrowRight,
  CalendarClock,
  Compass,
  LoaderCircle,
  MapPin,
  Navigation,
  ShieldAlert,
  ShieldCheck,
  Truck,
} from "lucide-react";
import type { ChangeEvent, FormEvent } from "react";

import type { RoutePlanResponse } from "../../lib/api";
import RouteResults from "./RouteResults";

type BackendStatus = "checking" | "connected" | "error";

interface RoutePlannerFormProps {
  backendStatus: BackendStatus;
  origin: string;
  setOrigin: (value: string) => void;
  destination: string;
  setDestination: (value: string) => void;
  departureTime: string;
  setDepartureTime: (value: string) => void;
  truckLoad: string;
  setTruckLoad: (value: string) => void;
  loading: boolean;
  error: string;
  result: RoutePlanResponse | null;
  handlePlanRoute: (event: FormEvent<HTMLFormElement>) => void;
  getLocalDateTime: () => string;
  recommendedRoute: RoutePlanResponse["routes"][number] | undefined;
  getSafetyMessage: (result: RoutePlanResponse) => string;
  formatNumber: (value: number, decimals?: number) => string;
  formatDuration: (seconds: number) => string;
  formatArrival: (value: string) => string;
  getRiskClass: (risk: string) => string;
  riskCategories: string[];
}

export default function RoutePlannerForm({
  backendStatus,
  origin,
  setOrigin,
  destination,
  setDestination,
  departureTime,
  setDepartureTime,
  truckLoad,
  setTruckLoad,
  loading,
  error,
  result,
  handlePlanRoute,
  getLocalDateTime,
  recommendedRoute,
  getSafetyMessage,
  formatNumber,
  formatDuration,
  formatArrival,
  getRiskClass,
  riskCategories,
}: RoutePlannerFormProps) {
  const handleOriginChange = (event: ChangeEvent<HTMLInputElement>) =>
    setOrigin(event.target.value);

  const handleDestinationChange = (event: ChangeEvent<HTMLInputElement>) =>
    setDestination(event.target.value);

  const handleDepartureChange = (event: ChangeEvent<HTMLInputElement>) =>
    setDepartureTime(event.target.value);

  const handleLoadChange = (event: ChangeEvent<HTMLInputElement>) =>
    setTruckLoad(event.target.value);

  return (
    <section className="planner-section section-wrap" id="planner">
      <motion.div
        className="planner-banner"
        initial={{ opacity: 0, y: 22 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.25 }}
        transition={{ duration: 0.6 }}
      >
        <div className="planner-banner-icon">
          <Truck size={28} />
        </div>

        <div className="planner-banner-copy">
          <span className="section-kicker">
            YOUR NEXT JOURNEY STARTS HERE
          </span>
          <h2>Plan a smarter route.</h2>
          <p>
            Enter your journey details to request available routes and
            evaluate forecast conditions along the way.
          </p>
        </div>

        <div className="planner-banner-action">
          <span className="coming-soon">
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
              ? "API CONNECTED"
              : backendStatus === "error"
                ? "API OFFLINE"
                : "CHECKING API"}
          </span>

          <span className="planner-action-note">
            Real results depend on routing and forecast provider availability.
          </span>
        </div>
      </motion.div>

      <div className="route-planner">
        <div className="route-planner-heading">
          <span className="section-kicker">JOURNEY DETAILS</span>
          <h3>Where are you heading?</h3>
          <p>
            Enter US locations and a future departure time. Use a city and
            state to help the location search.
          </p>
        </div>

        <form onSubmit={handlePlanRoute}>
          <div className="route-form-grid">
            <div className="route-field">
              <label htmlFor="route-origin">Origin</label>
              <input
                id="route-origin"
                name="origin"
                value={origin}
                onChange={handleOriginChange}
                placeholder="New York, NY, USA"
                autoComplete="off"
                maxLength={200}
                required
                disabled={loading}
              />
              <span className="route-field-hint">
                <MapPin size={13} style={{ display: "inline" }} /> Starting
                city or address in the USA
              </span>
            </div>

            <div className="route-field">
              <label htmlFor="route-destination">Destination</label>
              <input
                id="route-destination"
                name="destination"
                value={destination}
                onChange={handleDestinationChange}
                placeholder="Chicago, IL, USA"
                autoComplete="off"
                maxLength={200}
                required
                disabled={loading}
              />
              <span className="route-field-hint">
                <Navigation size={13} style={{ display: "inline" }} /> Your
                intended destination in the USA
              </span>
            </div>

            <div className="route-field">
              <label htmlFor="route-departure">
                Departure date and time
              </label>
              <input
                id="route-departure"
                name="departure_time"
                type="datetime-local"
                value={departureTime}
                onChange={handleDepartureChange}
                min={getLocalDateTime()}
                required
                disabled={loading}
              />
              <span className="route-field-hint">
                <CalendarClock size={13} style={{ display: "inline" }} />{" "}
                Your local time will be converted to UTC for the API
              </span>
            </div>

            <div className="route-field">
              <label htmlFor="route-load">Truck load (pounds)</label>
              <input
                id="route-load"
                name="truck_load_lbs"
                type="number"
                value={truckLoad}
                onChange={handleLoadChange}
                min="0.01"
                max="1000000"
                step="0.01"
                required
                disabled={loading}
              />
              <span className="route-field-hint">
                <Truck size={13} style={{ display: "inline" }} /> Enter the
                cargo load used by the risk evaluation
              </span>
            </div>
          </div>

          <div className="route-form-actions">
            <button
              className="route-submit-button"
              type="submit"
              disabled={loading || backendStatus !== "connected"}
            >
              {loading ? (
                <>
                  <LoaderCircle size={18} className="route-spinner" />
                  Calculating route…
                </>
              ) : (
                <>
                  <Compass size={18} />
                  Calculate route
                  <ArrowRight size={17} />
                </>
              )}
            </button>

            <span className="route-field-hint">
              <ShieldCheck size={14} style={{ display: "inline" }} />{" "}
              Results are estimates, not a guarantee of road safety.
            </span>
          </div>
        </form>

        {backendStatus === "error" && (
          <div className="route-form-message error" role="status">
            The Django backend is unavailable. Start the backend server and
            check your frontend API URL before submitting.
          </div>
        )}

        {error && (
          <div className="route-form-message error" role="alert">
            <ShieldAlert size={17} style={{ display: "inline" }} /> {error}
          </div>
        )}

        {result && (
          <RouteResults
            result={result}
            recommendedRoute={recommendedRoute}
            getSafetyMessage={getSafetyMessage}
            formatNumber={formatNumber}
            formatDuration={formatDuration}
            formatArrival={formatArrival}
            getRiskClass={getRiskClass}
            riskCategories={riskCategories}
          />
        )}
      </div>
    </section>
  );
}
