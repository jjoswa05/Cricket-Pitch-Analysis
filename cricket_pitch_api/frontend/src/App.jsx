import { useEffect, useState } from "react";
import { getStatus, predict } from "./api.js";
import UploadPanel from "./components/UploadPanel.jsx";
import Results from "./components/Results.jsx";

export default function App() {
  const [status, setStatus] = useState({ state: "checking", text: "checking API…" });
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  useEffect(() => {
    getStatus()
      .then((j) => setStatus({ state: "ok", text: `API online · ${j.model || ""}` }))
      .catch(() => setStatus({ state: "bad", text: "API offline" }));
  }, []);

  const choose = (f) => {
    if (f && !f.type.startsWith("image/")) return setError("Please choose an image file.");
    setFile(f); setData(null); setError("");
  };

  const analyze = async () => {
    setLoading(true); setError("");
    try { setData(await predict(file)); }
    catch (e) { setError(e.message || "Request failed"); }
    finally { setLoading(false); }
  };

  return (
    <>
      <header>
        <div className="brand"><span className="stump" />Pitch<b>Analyzer</b></div>
        <div className={`status ${status.state}`}>{status.text}</div>
      </header>
      <main>
        <UploadPanel file={file} detections={data?.detections} loading={loading} error={error}
                     onChoose={choose} onAnalyze={analyze} />
        {data && <Results data={data} />}
      </main>
    </>
  );
}
