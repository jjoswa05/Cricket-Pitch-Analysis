import { useEffect, useMemo, useRef, useState } from "react";

export default function UploadPanel({ file, detections, loading, error, onChoose, onAnalyze }) {
  const input = useRef(null);
  const img = useRef(null);
  const canvas = useRef(null);
  const [over, setOver] = useState(false);
  const url = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => () => url && URL.revokeObjectURL(url), [url]);

  // Draw YOLO boxes (backend returns original-image pixel coords)
  const draw = () => {
    const im = img.current, c = canvas.current;
    if (!im || !c) return;
    c.width = im.naturalWidth; c.height = im.naturalHeight;
    const g = c.getContext("2d");
    g.clearRect(0, 0, c.width, c.height);
    const lw = Math.max(3, c.width / 200);
    g.lineWidth = lw; g.font = `${lw * 6}px sans-serif`;
    (detections || []).forEach(({ bounding_box: b, class_name, confidence }) => {
      g.strokeStyle = "#e2573f"; g.strokeRect(b.x1, b.y1, b.x2 - b.x1, b.y2 - b.y1);
      const t = `${class_name} ${(confidence * 100).toFixed(0)}%`;
      g.fillStyle = "#e2573f";
      g.fillRect(b.x1, Math.max(0, b.y1 - lw * 8), g.measureText(t).width + lw * 3, lw * 8);
      g.fillStyle = "#fff"; g.fillText(t, b.x1 + lw * 1.5, Math.max(lw * 6, b.y1 - lw * 1.8));
    });
  };
  useEffect(draw, [detections, url]);

  return (
    <section className="panel upload">
      <h1>Read the pitch. Pick the attack.</h1>
      <p className="sub">Upload a pitch photo. YOLO detects the strip, then a rule-based layer recommends Pace, Seam or Spin.</p>

      <div
        className={`drop${over ? " over" : ""}`} tabIndex={0}
        onClick={() => input.current.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && input.current.click()}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); onChoose(e.dataTransfer.files[0]); }}
      >
        <input ref={input} type="file" accept="image/*" hidden onChange={(e) => onChoose(e.target.files[0])} />
        {url ? (
          <div className="stage">
            <img ref={img} src={url} alt="Pitch preview" onLoad={draw} />
            <canvas ref={canvas} />
          </div>
        ) : (<div><strong>Drop an image</strong> or click to browse</div>)}
      </div>

      <div className="actions">
        <button disabled={!file || loading} onClick={onAnalyze}>{loading ? "Analyzing…" : "Analyze pitch"}</button>
        {file && <button className="ghost" onClick={() => { input.current.value = ""; onChoose(null); }}>Clear</button>}
      </div>
      {error && <div className="error">{error}</div>}
    </section>
  );
}
