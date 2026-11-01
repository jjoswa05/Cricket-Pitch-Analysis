const API = "/api";

export async function getStatus() {
  const r = await fetch(`${API}/`);
  if (!r.ok) throw new Error("offline");
  return r.json();
}

export async function predict(file) {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`${API}/predict`, { method: "POST", body: fd });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail ? JSON.stringify(data.detail) : `Server error ${r.status}`);
  return data;
}
