
import { Suspense, lazy } from "react";
import { motion } from "motion/react";
import {
  CheckCircle2,
  CloudRain,
  MapPin,
  MapPinned,
  ShieldAlert,
} from "lucide-react";

import type { PlannedRoute, RoutePlanResponse } from "../../lib/api";

const RouteMap = lazy(() => import("../RouteMap"));

interface RouteResultsProps {
  result: RoutePlanResponse;
  recommendedRoute: PlannedRoute | undefined;
  getSafetyMessage: (result: RoutePlanResponse) => string;
  formatNumber: (value: number, decimals?: number) => string;
  formatDuration: (seconds: number) => string;
  formatArrival: (value: string) => string;
  getRiskClass: (risk: string) => string;
  riskCategories: string[];
}

export default function RouteResults({
  result,
  recommendedRoute,
  getSafetyMessage,
  formatNumber,
  formatDuration,
  formatArrival,
  getRiskClass,
  riskCategories,
}: RouteResultsProps) {
  return (
    <section
      className="route-results"
      id="route-results"
      aria-live="polite"
    >
      <span className="section-kicker">ANALYSIS RESULTS</span>
      <h3>Your route analysis</h3>

      <div
        className={`route-form-message ${
          result.recommended_route_id ? "success" : "error"
        }`}
      >
        <strong>
          {result.safety_status === "no_safe_route_available"
            ? "No route satisfies the current safety rules"
            : result.recommended_route_id
              ? `Recommended route: ${result.recommended_route_id}`
              : "No route recommendation available"}
        </strong>

        <p>{getSafetyMessage(result)}</p>

        {result.routes.length === 1 && (
          <p>
            Only one route alternative was returned by the routing provider
            for this request.
          </p>
        )}
      </div>

      {recommendedRoute && (
        <div className="route-result-stats" style={{ marginTop: 18 }}>
          <strong>Recommended route overview</strong>
          <span>
            Distance:{" "}
            <strong>
              {formatNumber(recommendedRoute.distance_miles)} miles
            </strong>
          </span>
          <span>
            Estimated driving time:{" "}
            <strong>
              {formatDuration(recommendedRoute.duration_seconds)}
            </strong>
          </span>
          <span>
            Checkpoints:{" "}
            <strong>{recommendedRoute.checkpoints.length}</strong>
          </span>
        </div>
      )}

      <div className="route-results-grid">
        {result.routes.map((route) => {
          const recommended =
            route.route_id === result.recommended_route_id;

          return (
            <motion.article
              className={`route-result-card ${
                recommended ? "recommended" : ""
              }`}
              key={route.route_id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
            >
              {recommended && (
                <span className="route-recommendation">
                  <CheckCircle2 size={13} /> Recommended
                </span>
              )}

              {route.has_no_travel && (
                <span className="route-recommendation">
                  <ShieldAlert size={13} /> No Travel risk
                </span>
              )}

              <h4>{route.route_id}</h4>

              <div className="route-result-stats">
                <span>
                  Distance:{" "}
                  <strong>{formatNumber(route.distance_miles)} mi</strong>
                </span>
                <span>
                  Driving time:{" "}
                  <strong>{formatDuration(route.duration_seconds)}</strong>
                </span>
                <span>
                  Checkpoints: <strong>{route.checkpoints.length}</strong>
                </span>
                <span>
                  Average risk score:{" "}
                  <strong>{formatNumber(route.average_risk, 2)} / 5</strong>
                </span>
              </div>

              <div className="route-risk-breakdown">
                <strong>Risk by distance</strong>

                {riskCategories.map((category) => (
                  <div className="route-risk-row" key={category}>
                    <span
                      className={`risk-dot ${getRiskClass(category)}`}
                    />
                    <span>{category}</span>
                    <strong>
                      {formatNumber(route.risk_miles?.[category] ?? 0)} mi
                    </strong>
                  </div>
                ))}
              </div>

              <div className="route-checkpoints">
                <strong>Checkpoint details</strong>

                {route.checkpoints.slice(0, 5).map((checkpoint) => (
                  <div
                    className="route-checkpoint-row"
                    key={`${route.route_id}-${checkpoint.checkpoint_index}`}
                  >
                    <span>
                      <MapPin size={14} />
                      {formatNumber(checkpoint.distance_miles)} mi
                    </span>

                    <span
                      className={`risk-label ${getRiskClass(
                        checkpoint.final_risk,
                      )}`}
                    >
                      {checkpoint.final_risk}
                    </span>

                    <span>{formatArrival(checkpoint.arrival_time)}</span>
                  </div>
                ))}

                {route.checkpoints.length > 5 && (
                  <p className="route-field-hint">
                    Showing the first 5 of {route.checkpoints.length}
                    {" "}checkpoints. The full checkpoint list will be
                    available in the interactive map view.
                  </p>
                )}
              </div>

              {route.geometry?.coordinates?.length > 0 && (
                <p className="route-field-hint">
                  <MapPinned size={14} style={{ display: "inline" }} /> Route
                  geometry loaded: {route.geometry.coordinates.length}
                  {" "}coordinates. View this route on the interactive map
                  below.
                </p>
              )}
            </motion.article>
          );
        })}
      </div>

      <Suspense
        fallback={
          <div className="route-map-empty" role="status">
            Loading interactive map…
          </div>
        }
      >
        <RouteMap
          routes={result.routes}
          recommendedRouteId={result.recommended_route_id}
        />
      </Suspense>

      <p className="route-field-hint" style={{ marginTop: 18 }}>
        <CloudRain size={14} style={{ display: "inline" }} /> Weather forecasts
        and arrival times are estimates. The routing provider currently uses a
        passenger-car profile, not a truck-specific routing profile. Follow
        official road and weather safety guidance.
      </p>
    </section>
  );
}
