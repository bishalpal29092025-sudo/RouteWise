import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import type { PlannedRoute } from "../lib/api";

import "leaflet/dist/leaflet.css";

interface RouteMapProps {
  routes: PlannedRoute[];
  recommendedRouteId: string | null;
}

const ROUTE_COLORS = ["#22d3ee", "#a78bfa", "#fb923c"];
const OVERLAY_RISKS = ["high", "severe", "no travel"];

function FitRoutes({ routes }: { routes: PlannedRoute[] }) {
  const map = useMap();

  useEffect(() => {
    const points = routes.flatMap((route) =>
      route.geometry.coordinates.map(
        ([longitude, latitude]) =>
          [latitude, longitude] as L.LatLngTuple
      )
    );

    if (points.length > 0) {
      map.fitBounds(L.latLngBounds(points), {
        padding: [35, 35],
      });
    }
  }, [map, routes]);

  return null;
}

function getRiskColor(risk: string): string {
  switch (risk.toLowerCase()) {
    case "low":
      return "#22c55e";
    case "moderate":
      return "#eab308";
    case "high":
      return "#f97316";
    case "severe":
      return "#ef4444";
    case "no travel":
      return "#a855f7";
    default:
      return "#94a3b8";
  }
}

function getOverlayRadius(risk: string): number {
  switch (risk.toLowerCase()) {
    case "no travel":
      return 24;
    case "severe":
      return 19;
    case "high":
      return 14;
    default:
      return 0;
  }
}

function formatMeasurement(value: number, unit: string): string {
  return `${Number.isFinite(value) ? value : 0} ${unit}`;
}

export default function RouteMap({
  routes,
  recommendedRouteId,
}: RouteMapProps) {
  const validRoutes = useMemo(
    () =>
      routes.filter(
        (route) => route.geometry.coordinates.length > 0
      ),
    [routes]
  );

  const recommendedRoute = validRoutes.find(
    (route) => route.route_id === recommendedRouteId
  );

  const sliderRoute = recommendedRoute ?? validRoutes[0];

  // Store the selected checkpoint together with its route ID.
  const [sliderSelection, setSliderSelection] = useState({
    routeId: "",
    index: 0,
  });

  // Start at checkpoint zero whenever the slider route changes.
  // Clamp the index if the selected route has fewer checkpoints.
  const selectedCheckpointIndex =
    sliderSelection.routeId === sliderRoute?.route_id
      ? Math.min(
          sliderSelection.index,
          Math.max(
            0,
            (sliderRoute?.checkpoints.length ?? 1) - 1
          )
        )
      : 0;

  const selectedCheckpoint =
    sliderRoute?.checkpoints[selectedCheckpointIndex];

  if (validRoutes.length === 0) {
    return (
      <div className="route-map-empty">
        No route geometry is available to display.
      </div>
    );
  }

  const firstCoordinate = validRoutes[0].geometry.coordinates[0];

  return (
    <section className="route-map-section">
      <div className="route-map-heading">
        <div>
          <span className="eyebrow">LIVE ROUTE GEOMETRY</span>
          <h3>Explore your route</h3>
          <p>
            Explore checkpoint forecasts, compare route risks, and
            move through the recommended route&apos;s estimated journey.
          </p>
        </div>

        <span className="route-map-badge">
          {validRoutes.length} route
          {validRoutes.length === 1 ? "" : "s"}
        </span>
      </div>

      {/* Checkpoint forecast timeline */}
      {sliderRoute && sliderRoute.checkpoints.length > 0 && (
        <div
          className="route-result-stats"
          style={{ marginBottom: 16, padding: 18 }}
        >
          <strong>Forecast timeline</strong>

          <label htmlFor="checkpoint-timeline">
            Checkpoint {selectedCheckpointIndex + 1} of{" "}
            {sliderRoute.checkpoints.length}
          </label>

          <input
            id="checkpoint-timeline"
            type="range"
            min={0}
            max={sliderRoute.checkpoints.length - 1}
            step={1}
            value={selectedCheckpointIndex}
            onChange={(event) =>
              setSliderSelection({
                routeId: sliderRoute.route_id,
                index: Number(event.target.value),
              })
            }
            style={{
              width: "100%",
              accentColor: "#22d3ee",
            }}
            aria-label="Select a route forecast checkpoint"
          />

          {selectedCheckpoint && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(130px, 1fr))",
                gap: 12,
              }}
            >
              <div>
                <small>Distance along route</small>
                <div>
                  <strong>
                    {selectedCheckpoint.distance_miles.toFixed(1)} mi
                  </strong>
                </div>
              </div>

              <div>
                <small>Estimated arrival</small>
                <div>
                  <strong>
                    {new Date(
                      selectedCheckpoint.arrival_time
                    ).toLocaleString()}
                  </strong>
                </div>
              </div>

              <div>
                <small>Overall risk</small>
                <div>
                  <strong
                    style={{
                      color: getRiskColor(
                        selectedCheckpoint.final_risk
                      ),
                    }}
                  >
                    {selectedCheckpoint.final_risk}
                  </strong>
                </div>
              </div>

              <div>
                <small>Wind</small>
                <div>
                  <strong>
                    {formatMeasurement(
                      selectedCheckpoint.weather.wind_mph,
                      "mph"
                    )}
                  </strong>
                </div>
              </div>

              <div>
                <small>Rain</small>
                <div>
                  <strong>
                    {formatMeasurement(
                      selectedCheckpoint.weather.rain_inches,
                      "in"
                    )}
                  </strong>
                </div>
              </div>

              <div>
                <small>Snow</small>
                <div>
                  <strong>
                    {formatMeasurement(
                      selectedCheckpoint.weather.snowfall_inches,
                      "in"
                    )}
                  </strong>
                </div>
              </div>
            </div>
          )}

          <p className="route-field-hint">
            The slider selects actual forecast checkpoints. Weather
            conditions between checkpoints are not interpolated.
          </p>
        </div>
      )}

      {/* Interactive route map */}
      <div className="route-map-frame">
        <MapContainer
          center={[
            firstCoordinate[1],
            firstCoordinate[0],
          ]}
          zoom={5}
          scrollWheelZoom
          className="route-leaflet-map"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <FitRoutes routes={validRoutes} />

          {/* Translucent overlays for higher-risk checkpoints */}
          {validRoutes.map((route) =>
            route.checkpoints
              .filter((checkpoint) =>
                OVERLAY_RISKS.includes(
                  checkpoint.final_risk.toLowerCase()
                )
              )
              .map((checkpoint) => {
                const color = getRiskColor(
                  checkpoint.final_risk
                );

                return (
                  <CircleMarker
                    key={`weather-overlay-${route.route_id}-${checkpoint.checkpoint_index}`}
                    center={[
                      checkpoint.latitude,
                      checkpoint.longitude,
                    ]}
                    radius={getOverlayRadius(
                      checkpoint.final_risk
                    )}
                    interactive={false}
                    pathOptions={{
                      color,
                      fillColor: color,
                      fillOpacity: 0.16,
                      opacity: 0.3,
                      weight: 1,
                    }}
                  />
                );
              })
          )}

          {/* Route lines and forecast checkpoints */}
          {validRoutes.map((route, routeIndex) => {
            const isRecommended =
              route.route_id === recommendedRoute?.route_id;

            const routeColor =
              ROUTE_COLORS[
                routeIndex % ROUTE_COLORS.length
              ];

            const linePositions =
              route.geometry.coordinates.map(
                ([longitude, latitude]) =>
                  [latitude, longitude] as L.LatLngTuple
              );

            return (
              <div key={route.route_id}>
                <Polyline
                  positions={linePositions}
                  pathOptions={{
                    color: isRecommended
                      ? "#22d3ee"
                      : routeColor,
                    weight: isRecommended ? 6 : 4,
                    opacity: isRecommended ? 0.95 : 0.7,
                  }}
                />

                {route.checkpoints.map((checkpoint) => {
                  const isSelected =
                    route.route_id === sliderRoute?.route_id &&
                    checkpoint.checkpoint_index ===
                      selectedCheckpoint?.checkpoint_index;

                  const riskColor = getRiskColor(
                    checkpoint.final_risk
                  );

                  return (
                    <CircleMarker
                      key={`${route.route_id}-${checkpoint.checkpoint_index}`}
                      center={[
                        checkpoint.latitude,
                        checkpoint.longitude,
                      ]}
                      radius={
                        isSelected ? 9 : isRecommended ? 6 : 4
                      }
                      pathOptions={{
                        color: isSelected
                          ? "#ffffff"
                          : riskColor,
                        fillColor: riskColor,
                        fillOpacity: isSelected ? 1 : 0.9,
                        weight: isSelected ? 4 : 2,
                      }}
                    >
                      <Popup>
                        <div>
                          <strong>
                            Checkpoint{" "}
                            {checkpoint.checkpoint_index + 1}
                          </strong>
                          <br />

                          Distance:{" "}
                          {checkpoint.distance_miles.toFixed(1)} miles
                          <br />

                          Risk:{" "}
                          <strong>
                            {checkpoint.final_risk}
                          </strong>
                          <br />

                          Arrival:{" "}
                          {new Date(
                            checkpoint.arrival_time
                          ).toLocaleString()}
                          <br />

                          Wind:{" "}
                          {formatMeasurement(
                            checkpoint.weather.wind_mph,
                            "mph"
                          )}
                          <br />

                          Rain:{" "}
                          {formatMeasurement(
                            checkpoint.weather.rain_inches,
                            "in"
                          )}
                          <br />

                          Snow:{" "}
                          {formatMeasurement(
                            checkpoint.weather.snowfall_inches,
                            "in"
                          )}
                          <br />

                          Forecast:{" "}
                          {new Date(
                            checkpoint.weather.forecast_time
                          ).toLocaleString()}
                          <br />

                          Provider: {checkpoint.weather.provider}
                        </div>
                      </Popup>
                    </CircleMarker>
                  );
                })}
              </div>
            );
          })}
        </MapContainer>
      </div>

      {/* Risk legend */}
      <div className="route-map-legend">
        {[
          ["#22c55e", "Low"],
          ["#eab308", "Moderate"],
          ["#f97316", "High"],
          ["#ef4444", "Severe"],
          ["#a855f7", "No Travel"],
        ].map(([color, label]) => (
          <span key={label}>
            <i style={{ backgroundColor: color }} />
            {label}
          </span>
        ))}
      </div>

      <p className="route-field-hint">
        The translucent overlay highlights evaluated high-risk
        checkpoints. It is a checkpoint-based risk visualization,
        not a continuous weather forecast map. Route distances,
        arrival times, and forecasts are estimates.
      </p>
    </section>
  );
}
