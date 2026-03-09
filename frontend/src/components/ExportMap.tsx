"use client";
import { useState, useMemo } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";

const GEO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

// Map common country names to ISO 3166-1 alpha-3 codes
const COUNTRY_TO_ISO: Record<string, string> = {
  "United States": "USA", "USA": "USA", "United States of America": "USA",
  "United Kingdom": "GBR", "UK": "GBR",
  "China": "CHN", "Germany": "DEU", "Japan": "JPN", "France": "FRA",
  "India": "IND", "Italy": "ITA", "Canada": "CAN", "Australia": "AUS",
  "Brazil": "BRA", "South Korea": "KOR", "Korea, Republic of": "KOR",
  "Russia": "RUS", "Russian Federation": "RUS",
  "Mexico": "MEX", "Spain": "ESP", "Indonesia": "IDN",
  "Netherlands": "NLD", "Saudi Arabia": "SAU", "Turkey": "TUR",
  "Switzerland": "CHE", "Poland": "POL", "Sweden": "SWE",
  "Belgium": "BEL", "Argentina": "ARG", "Thailand": "THA",
  "Austria": "AUT", "Norway": "NOR", "Iran": "IRN",
  "UAE": "ARE", "United Arab Emirates": "ARE",
  "Nigeria": "NGA", "Ireland": "IRL", "Israel": "ISR",
  "South Africa": "ZAF", "Singapore": "SGP", "Malaysia": "MYS",
  "Philippines": "PHL", "Denmark": "DNK", "Colombia": "COL",
  "Finland": "FIN", "Chile": "CHL", "Bangladesh": "BGD",
  "Egypt": "EGY", "Vietnam": "VNM", "Viet Nam": "VNM",
  "Czech Republic": "CZE", "Czechia": "CZE",
  "Portugal": "PRT", "Romania": "ROU", "New Zealand": "NZL",
  "Peru": "PER", "Iraq": "IRQ", "Greece": "GRC",
  "Qatar": "QAT", "Kazakhstan": "KAZ", "Algeria": "DZA",
  "Hungary": "HUN", "Kuwait": "KWT", "Morocco": "MAR",
  "Ecuador": "ECU", "Ukraine": "UKR", "Slovakia": "SVK",
  "Sri Lanka": "LKA", "Kenya": "KEN", "Ethiopia": "ETH",
  "Tanzania": "TZA", "Ghana": "GHA", "Pakistan": "PAK",
  "Myanmar": "MMR", "Nepal": "NPL", "Cambodia": "KHM",
  "Oman": "OMN", "Luxembourg": "LUX", "Bulgaria": "BGR",
  "Croatia": "HRV", "Lithuania": "LTU", "Slovenia": "SVN",
  "Latvia": "LVA", "Estonia": "EST", "Serbia": "SRB",
  "Bahrain": "BHR", "Jordan": "JOR", "Tunisia": "TUN",
  "Lebanon": "LBN", "Uruguay": "URY", "Bolivia": "BOL",
  "Paraguay": "PRY", "Costa Rica": "CRI", "Panama": "PAN",
  "Guatemala": "GTM", "Dominican Republic": "DOM",
  "Honduras": "HND", "El Salvador": "SLV", "Nicaragua": "NIC",
  "Cuba": "CUB", "Jamaica": "JAM", "Trinidad and Tobago": "TTO",
  "Iceland": "ISL", "Malta": "MLT", "Cyprus": "CYP",
  "Georgia": "GEO", "Armenia": "ARM", "Azerbaijan": "AZE",
  "Uzbekistan": "UZB", "Mongolia": "MNG", "Laos": "LAO",
  "Brunei": "BRN", "Taiwan": "TWN", "Hong Kong": "HKG",
  "Macao": "MAC",
};

// Stable color palette for HS codes
const HS_COLORS = [
  { base: "#3b82f6", light: "#93c5fd" },  // blue
  { base: "#10b981", light: "#6ee7b7" },  // emerald
  { base: "#f59e0b", light: "#fcd34d" },  // amber
  { base: "#ef4444", light: "#fca5a5" },  // red
  { base: "#8b5cf6", light: "#c4b5fd" },  // violet
  { base: "#ec4899", light: "#f9a8d4" },  // pink
  { base: "#06b6d4", light: "#67e8f9" },  // cyan
  { base: "#84cc16", light: "#bef264" },  // lime
];

export interface MapMarket {
  country: string;
  hs_code: string;
  product_description?: string | null;
  opportunity_score: number | null;
  total_import?: number | null;
  avg_growth_5y?: number | null;
}

interface ExportMapProps {
  data: MapMarket[];
  compact?: boolean; // dashboard mode
}

export default function ExportMap({ data, compact = false }: ExportMapProps) {
  const [tooltip, setTooltip] = useState<{
    x: number; y: number; items: MapMarket[];
  } | null>(null);

  // Build lookup: ISO code -> list of market entries
  const { countryMap, hsCodeColors, hsCodes, hsDescriptions } = useMemo(() => {
    const codes = [...new Set(data.map((d) => d.hs_code))].sort();
    const colorMap: Record<string, typeof HS_COLORS[0]> = {};
    codes.forEach((c, i) => { colorMap[c] = HS_COLORS[i % HS_COLORS.length]; });

    // Build description map from data
    const descMap: Record<string, string> = {};
    for (const entry of data) {
      if (entry.product_description && !descMap[entry.hs_code]) {
        descMap[entry.hs_code] = entry.product_description;
      }
    }

    const cMap = new Map<string, MapMarket[]>();
    for (const entry of data) {
      const iso = COUNTRY_TO_ISO[entry.country.trim()];
      console.log("[DEBUG DATA] Country → ISO:", entry.country, "→", iso);
      if (!iso) continue;
      if (!cMap.has(iso)) cMap.set(iso, []);
      cMap.get(iso)!.push(entry);
    }
    return { countryMap: cMap, hsCodeColors: colorMap, hsCodes: codes, hsDescriptions: descMap };
  }, [data]);

  console.log("[DEBUG COUNTRY MAP KEYS]", [...countryMap.keys()]);

  const getCountryFill = (iso: string) => {
    const items = countryMap.get(iso);
    if (!items || items.length === 0) return "var(--bg-card)";
    // Use the HS code with the highest opportunity score for color
    const best = items.reduce((a, b) =>
      (a.opportunity_score ?? 0) >= (b.opportunity_score ?? 0) ? a : b
    );
    const color = hsCodeColors[best.hs_code];
    const score = best.opportunity_score ?? 0;
    // Interpolate opacity based on score (0.3 to 1.0)
    const opacity = 0.3 + score * 0.7;
    return adjustOpacity(color.base, opacity);
  };

  const formatImport = (val: number | null | undefined) => {
    if (!val) return "N/A";
    if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
    if (val >= 1e6) return `$${(val / 1e6).toFixed(0)}M`;
    return `$${val.toLocaleString()}`;
  };

  return (
    <div className="relative">
      {/* Legend */}
      {hsCodes.length > 0 && (
        <div className={`flex flex-wrap gap-3 ${compact ? "mb-2" : "mb-4"}`}>
          {hsCodes.map((code) => (
            <div key={code} className="flex items-center gap-1.5 text-xs">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: hsCodeColors[code].base }}
              />
              <span className="text-[var(--text-secondary)]">
                HS {code}{hsDescriptions[code] ? ` · ${hsDescriptions[code]}` : ""}
              </span>
            </div>
          ))}
        </div>
      )}

      <ComposableMap
        projectionConfig={{ scale: compact ? 120 : 150 }}
        style={{ width: "100%", height: compact ? 280 : 420 }}
      >
        <ZoomableGroup>
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map((geo) => {
                // const iso = 
                // geo.properties.ISO_A3 && geo.properties.ISO_A3 !== "-99"
                //   ? geo.properties.ISO_A3
                //   : geo.properties.ADM0_A3;

                // const iso = geo.id;

                const countryName = geo.properties.name || geo.properties.NAME;
                
                const iso = COUNTRY_TO_ISO[countryName];

                // console.log(
                //   geo.properties.NAME,
                //   geo.properties.ISO_A3,
                //   geo.properties.ADM0_A3
                // );

                console.log( "[DEBUG] Mapping country:",
                  geo.properties.name,
                  geo.id
                );

                console.log(
                  "[DEBUG MATCH]",
                  countryName,
                  "→",
                  iso,
                  "→",
                  countryMap.get(iso)
                );
                const items = countryMap.get(iso);
                console.log("[DEBUG LOOKUP]", iso, items);
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={getCountryFill(iso)}
                    stroke="var(--border)"
                    strokeWidth={0.5}
                    style={{
                      hover: { fill: items ? "#fbbf24" : "var(--border)", cursor: items ? "pointer" : "default" },
                      pressed: { fill: items ? "#f59e0b" : "var(--border)" },
                    }}
                    onMouseEnter={(evt) => {
                      if (!items) return;
                      setTooltip({ x: evt.clientX, y: evt.clientY, items });
                    }}
                    onMouseLeave={() => setTooltip(null)}
                  />
                );
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-3 shadow-xl pointer-events-none max-w-xs"
          style={{ left: tooltip.x + 12, top: tooltip.y - 10 }}
        >
          <div className="font-semibold text-sm mb-1.5">
            {tooltip.items[0].country}
          </div>
          {tooltip.items.map((item) => (
            <div
              key={item.hs_code}
              className="text-xs space-y-0.5 mb-1 pb-1 border-b border-[var(--border)] last:border-0 last:mb-0 last:pb-0"
            >
              <div className="flex justify-between gap-4">
                <span style={{ color: hsCodeColors[item.hs_code]?.base }}>
                  HS {item.hs_code}{item.product_description ? ` · ${item.product_description}` : ""}
                </span>
                <span className="font-bold">
                  Score: {item.opportunity_score?.toFixed(2) ?? "N/A"}
                </span>
              </div>
              {!compact && (
                <>
                  <div className="flex justify-between gap-4 text-[var(--text-secondary)]">
                    <span>Imports</span>
                    <span>{formatImport(item.total_import)}</span>
                  </div>
                  <div className="flex justify-between gap-4 text-[var(--text-secondary)]">
                    <span>5Y Growth</span>
                    <span>
                      {item.avg_growth_5y
                        ? `${(item.avg_growth_5y * 100).toFixed(1)}%`
                        : "N/A"}
                    </span>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// function adjustOpacity(hex: string, opacity: number): string {
//   const r = parseInt(hex.slice(1, 3), 16);
//   const g = parseInt(hex.slice(3, 5), 16);
//   const b = parseInt(hex.slice(5, 7), 16);
//   // Blend with dark background (#0f172a)
//   const bg = { r: 15, g: 23, b: 42 };
//   const nr = Math.round(bg.r + (r - bg.r) * opacity);
//   const ng = Math.round(bg.g + (g - bg.g) * opacity);
//   const nb = Math.round(bg.b + (b - bg.b) * opacity);
//   return `rgb(${nr},${ng},${nb})`;
// }

function adjustOpacity(hex: string, opacity: number) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);

  const alpha = Math.max(0.35, opacity);

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
