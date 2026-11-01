import { useEffect, useState } from "react";

const COLORS = { Pace: "var(--pace)", Seam: "var(--seam)", Spin: "var(--spin)" };
const NOTES = {
  Pace: "Dry, firm surface with low roughness — favours fast bowlers.",
  Seam: "Grass cover / moisture signs — favours seam movement.",
  Spin: "Rough, cracked, dry surface — favours spinners.",
};

function Bar({ label, shown, pct, color }) {
  const [w, setW] = useState(0);
  useEffect(() => { const id = requestAnimationFrame(() => setW(Math.min(100, pct))); return () => cancelAnimationFrame(id); }, [pct]);
  return (
    <div className="row">
      <span>{label}</span>
      <div className="track"><div className="fill" style={{ width: `${w}%`, background: color }} /></div>
      <span>{shown}</span>
    </div>
  );
}

export default function Results({ data }) {
  const { bowling_recommendation: rec, pitch_analysis: a, detections = [] } = data;
  const max = a ? Math.max(1, ...Object.values(a.bowling_scores)) : 1;
  const features = a ? [["Grass", a.grass_score], ["Dryness", a.dryness_score], ["Roughness", a.roughness_score],
                        ["Cracks", a.crack_score], ["Moisture*", a.moisture_proxy]] : [];
  return (
    <section className="panel results">
      <div className="reco">
        <span className="label">Recommended bowling</span>
        <div className="reco-val" style={{ color: rec ? COLORS[rec] : "var(--muted)" }}>{rec || "No pitch detected"}</div>
        <div className="muted">{rec ? NOTES[rec] : "The model found no pitch above 0.25 confidence. Try a clearer, closer photo."}</div>
      </div>

      {a && (<>
        <h2>Bowling scores</h2>
        {Object.entries(a.bowling_scores).map(([k, v]) => {
          const n = k[0].toUpperCase() + k.slice(1);
          return <Bar key={k} label={n} shown={v} pct={(v / max) * 100} color={COLORS[n]} />;
        })}
        <h2>Pitch features <span className="muted small">(0–100, visual proxies)</span></h2>
        {features.map(([n, v]) => <Bar key={n} label={n} shown={v} pct={v} />)}
      </>)}

      <h2>Detections</h2>
      {detections.length
        ? detections.map((d, i) => <div className="det" key={i}><span>{d.class_name}</span><span>{(d.confidence * 100).toFixed(1)}%</span></div>)
        : <div className="muted">None</div>}
      <details><summary>Raw JSON</summary><pre>{JSON.stringify(data, null, 2)}</pre></details>
    </section>
  );
}
