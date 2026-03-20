import React from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";


const UTC_DATETIME_FORMATTER = new Intl.DateTimeFormat("en-GB", {
  timeZone: "UTC",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});


function formatTickLabel(value) {
  return UTC_DATETIME_FORMATTER.format(new Date(value));
}


function formatTooltipLabel(value) {
  return `${UTC_DATETIME_FORMATTER.format(new Date(value))} UTC`;
}


function GenerationChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-empty-state">
        No chart data available for the selected range.
      </div>
    );
  }

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height={380}>
        <LineChart
          data={data}
          margin={{ top: 10, right: 24, left: 0, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#d6e1ea" />
          <XAxis
            dataKey="startTime"
            tickFormatter={formatTickLabel}
            minTickGap={32}
            stroke="#4c6681"
          />
          <YAxis stroke="#4c6681" />
          <Tooltip
            labelFormatter={formatTooltipLabel}
            formatter={(value, name) => [value ?? "No value", name]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="actualGeneration"
            name="Actual"
            stroke="#1f77b4"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="forecastGeneration"
            name="Forecast"
            stroke="#2e8b57"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 4 }}
            connectNulls={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


export default GenerationChart;
