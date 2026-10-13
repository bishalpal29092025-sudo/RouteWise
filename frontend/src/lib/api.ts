const API_BASE_URL = 
    import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export interface HealthResponse {
    status: string,
    message: string,
    service: string,
}

export async function checkBackendHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health/`);

    if(!response.ok) {
        throw new Error(`Backend request failed: HTTP ${response.status}`);
    }

    return response.json() as Promise<HealthResponse>;
}

export interface RoutePlanRequest {
    origin: string;
    destination: string;
    departure_time: string;
    truck_load_lbs: string;
}


export interface CheckpointWeather {
    forecast_time: string;
    arrival_time: string;
    wind_mph: number;
    rain_inches: number;
    snowfall_inches: number;
    provider: string;
}

export interface RouteCheckpoint {
    checkpoint_index: number;
    distance_miles: number;
    latitude: number;
    longitude: number;
    arrival_time: string;

    weather: CheckpointWeather;

    wind_risk: string;
    rain_risk: string;
    snow_risk: string;
    load_risk: string;
    final_risk: string;
    risk_value: number;

    [key: string]: unknown;
}


export interface PlannedRoute {
    route_id: string;
    distance_miles: number;
    duration_seconds: number;
    checkpoints: RouteCheckpoint[];
    risk_miles: Record<string, number>;
    average_risk: number;
    has_no_travel: boolean;
    geometry: {
        type: string;
        coordinates: [number, number][];
    };
}

export interface RoutePlanResponse {
    status: string;
    safety_status: string;
    recommended_route_id: string | null;
    routes: PlannedRoute[];
}

export async function planRoute(
    requestData: RoutePlanRequest
): Promise<RoutePlanResponse> {
    const response = await fetch(`${API_BASE_URL}/route-plan/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
    });

    const data = await response.json();

    if (!response.ok) {
        const message =
            data?.detail ??
            data?.message ??
            "Unable to calculate the route.";

        throw new Error(
            typeof message === "string"
                ? message
                : JSON.stringify(message)
        );
    }

    return data as RoutePlanResponse;
}