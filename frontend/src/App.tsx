import { useState } from "react";

type Analysis = {
  width: number; height: number; channels: number; mean_grayscale: number;
  sharpness_laplacian_variance: number; histogram: Record<string, number[]>;
};
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function chooseFile(next?: File) {
    if (preview) URL.revokeObjectURL(preview);
    setFile(next ?? null); setPreview(next ? URL.createObjectURL(next) : null);
    setAnalysis(null); setError(null);
  }

  async function analyze() {
    if (!file) return;
    setBusy(true); setError(null); setAnalysis(null);
    try {
      const body = new FormData(); body.append("file", file);
      const response = await fetch(`${API_BASE}/api/v1/images/analyze`, { method: "POST", body });
      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail ?? `Request failed (${response.status})`);
      }
      setAnalysis(await response.json() as Analysis);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unexpected request error.");
    } finally { setBusy(false); }
  }

  return <main className="shell">
    <header className="topbar"><div className="brand">V</div><div><strong>VisionAI</strong><small>Computer Vision Workspace</small></div><span className="status">● API workspace</span></header>
    <section className="intro"><p className="eyebrow">IMAGE INTELLIGENCE / FOUNDATION</p><h1>Understand your images.</h1><p>Upload an image to inspect dimensions, luminance, sharpness and color distribution.</p></section>
    <section className="workspace">
      <article className="panel"><div className="heading"><div><p className="eyebrow">INPUT</p><h2>Image workspace</h2></div><span>01</span></div>
        <label className="dropzone"><input type="file" accept="image/jpeg,image/png,image/webp" onChange={e => chooseFile(e.target.files?.[0])}/>{preview ? <img src={preview} alt="Selected image preview"/> : <span><b className="upload">↑</b><strong>Choose an image</strong><small>JPEG, PNG or WebP</small></span>}</label>
        <div className="actions"><small>{file?.name ?? "No image selected"}</small><button disabled={!file || busy} onClick={analyze}>{busy ? "Analyzing…" : "Analyze image"}</button></div>
        {error && <p className="error" role="alert">{error}</p>}
      </article>
      <article className="panel"><div className="heading"><div><p className="eyebrow">OUTPUT</p><h2>Analysis results</h2></div><span>02</span></div>
        {!analysis ? <div className="empty">Analysis metrics appear here after processing.</div> : <>
          <div className="metrics"><Metric label="Dimensions" value={`${analysis.width} × ${analysis.height}`}/><Metric label="Channels" value={String(analysis.channels)}/><Metric label="Mean luminance" value={analysis.mean_grayscale.toFixed(2)}/><Metric label="Sharpness" value={analysis.sharpness_laplacian_variance.toFixed(2)}/></div>
          <div className="histograms">{Object.entries(analysis.histogram).map(([name,bins]) => <div key={name}><div className="hist-title"><b>{name}</b><small>16 bins</small></div><div className="bars">{bins.map((v,i)=><i key={i} style={{height:`${Math.max(3,v/Math.max(...bins,1)*100)}%`}}/>)}</div></div>)}</div>
        </>}
      </article>
    </section>
    <footer>VisionAI Platform <span>Foundation build · AI detection and live video are planned modules.</span></footer>
  </main>;
}
function Metric({label,value}:{label:string;value:string}) { return <div className="metric"><small>{label}</small><strong>{value}</strong></div>; }
