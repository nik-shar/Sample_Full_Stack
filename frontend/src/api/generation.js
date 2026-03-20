const LOCAL_API_BASE_URL = "http://127.0.0.1:8000";

function normalizeBaseUrl(baseUrl) {
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

function getApiBaseUrl() {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

  if (configuredBaseUrl) {
    return normalizeBaseUrl(configuredBaseUrl);
  }

  if (typeof window !== "undefined") {
    const { hostname } = window.location;

    if (hostname === "127.0.0.1" || hostname === "localhost") {
      return LOCAL_API_BASE_URL;
    }
  }

  return "";
}

function toUtcISOString(datetimeLocalValue) {
  return new Date(datetimeLocalValue).toISOString();
}

export async function fetchGenerationData({
  startTime,
  endTime,
  forecastHorizonHours,
}) {
  const params = new URLSearchParams({
    start_time: toUtcISOString(startTime),
    end_time: toUtcISOString(endTime),
    forecast_horizon_hours: String(forecastHorizonHours),
  });

  const apiBaseUrl = getApiBaseUrl();

  if (!apiBaseUrl) {
    throw new Error(
      "VITE_API_BASE_URL is not configured for this deployment."
    );
  }

  const response = await fetch(
    `${apiBaseUrl}/generation?${params.toString()}`
  );

  if (!response.ok) {
    let message = "Failed to fetch generation data.";

    try {
      const errorPayload = await response.json();
      message = errorPayload.detail || message;
    } catch {
      message = `Request failed with status ${response.status}`;
    }

    throw new Error(message);
  }

  return response.json();
}
