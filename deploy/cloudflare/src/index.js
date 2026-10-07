// The public website on Cloudflare's free plan: the static site and showcase
// (public/, assembled by build_site.py) plus the upload API. Uploads wait
// here until the render machine (web/worker.py on the owner's PC) picks them
// up, and their videos are kept here for an hour.
//
// One Durable Object ("main") holds everything in SQLite: jobs, the PDFs and
// videos (in chunks), and the daily counts. The render machine calls the
// /api/worker/* routes with WORKER_SECRET; visitors never see anything but a
// job's state, a plain-language phase and a generic message.
import { DurableObject } from "cloudflare:workers";
import LIMITS from "./limits.json";

const PHASES = ["Reading the manual", "Planning the assembly", "Animating in 3D", "Making the video"];
const FAILED_BUILDING = "Something went wrong while building the video. Try another manual.";
const OFFLINE = "Uploads are open when the render machine is on. It's off right now: watch the examples above, or try again later.";

const ONLINE_SECONDS = 60;            // the render machine polls every few seconds
const RUNNING_LOST_SECONDS = 5 * 60;  // a running job with no heartbeat this long has failed
const QUEUED_LOST_SECONDS = 10 * 60;  // a queued job while the machine stays offline
const CHUNK = 1024 * 1024;            // SQLite rows hold up to 2 MB

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
const problem = (detail, status) => json({ detail }, status);
const now = () => Date.now() / 1000;

// Browsers can only jump to a time in a video (clicking a step) when the
// server answers Range requests with 206; static assets don't, so videos
// are answered here.
function withRange(request, bytes, headers) {
  const range = /^bytes=(\d*)-(\d*)$/.exec(request.headers.get("range") || "");
  const base = { ...headers, "accept-ranges": "bytes" };
  if (!range || (!range[1] && !range[2])) {
    return new Response(bytes, { headers: { ...base, "content-length": String(bytes.length) } });
  }
  const size = bytes.length;
  let start = range[1] ? Number(range[1]) : Math.max(0, size - Number(range[2]));
  let end = range[1] && range[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
  if (start >= size || start > end) {
    return new Response(null, { status: 416, headers: { ...base, "content-range": `bytes */${size}` } });
  }
  return new Response(bytes.slice(start, end + 1), {
    status: 206,
    headers: { ...base, "content-range": `bytes ${start}-${end}/${size}`, "content-length": String(end - start + 1) },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.endsWith(".mp4") && !url.pathname.startsWith("/api/")) {
      const asset = await env.ASSETS.fetch(new Request(url, { method: "GET" }));
      if (!asset.ok) return asset;
      return withRange(request, new Uint8Array(await asset.arrayBuffer()), {
        "content-type": "video/mp4",
        "cache-control": "public, max-age=86400",
      });
    }
    if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);
    try {
      return await env.JOBS.get(env.JOBS.idFromName("main")).fetch(request);
    } catch {
      return problem("Something went wrong.", 500);
    }
  },
};

export class Jobs extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.lastSeen = 0; // the render machine's last call; memory only, so no writes
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, seq INTEGER, state TEXT, phase INTEGER DEFAULT 0,
        title TEXT DEFAULT '', message TEXT DEFAULT '', created REAL, touched REAL, finished REAL);
      CREATE TABLE IF NOT EXISTS blobs (
        job TEXT, kind TEXT, part INTEGER, data BLOB, PRIMARY KEY (job, kind, part));
      CREATE TABLE IF NOT EXISTS counts (
        day TEXT, visitor TEXT, n INTEGER, PRIMARY KEY (day, visitor));`);
  }

  async fetch(request) {
    try {
      this.request = request;
      this.tidy();
      const url = new URL(request.url);
      const parts = url.pathname.split("/").filter(Boolean); // ["api", ...]
      const method = request.method;

      if (parts[1] === "worker") {
        if (!this.authorised(request)) return problem("Not found.", 404);
        this.lastSeen = now();
        return await this.workerRoute(parts.slice(2), method, request);
      }
      if (method === "GET" && parts[1] === "limits") {
        return json({ pages: LIMITS.pages, mb: LIMITS.mb, online: this.online() });
      }
      if (method === "POST" && parts[1] === "jobs" && parts.length === 2) return await this.create(request);
      if (method === "GET" && parts[1] === "jobs" && parts.length === 3) return this.statusResponse(parts[2]);
      if (method === "GET" && parts[1] === "jobs" && parts[3] === "video") return this.video(parts[2]);
      return problem("Not found.", 404);
    } catch {
      return problem("Something went wrong.", 500);
    }
  }

  // ---------- visitors ----------

  online() {
    return now() - this.lastSeen < ONLINE_SECONDS;
  }

  async create(request) {
    if (!this.online()) return problem(OFFLINE, 503);

    const form = await request.formData().catch(() => null);
    const file = form && form.get("file");
    if (!file || typeof file === "string") return problem("Choose a PDF to upload.", 400);
    if (file.size > LIMITS.mb * 1024 * 1024) return problem(`The file is over ${LIMITS.mb} MB, the limit.`, 400);
    const bytes = new Uint8Array(await file.arrayBuffer());
    if (new TextDecoder().decode(bytes.slice(0, 5)) !== "%PDF-") return problem("That file isn't a readable PDF.", 400);
    // A quick count; the render machine checks again with a real PDF reader
    // (page objects can be compressed, so this can only find too many).
    const pages = (new TextDecoder("latin1").decode(bytes).match(/\/Type\s*\/Page(?![a-zA-Z])/g) || []).length;
    if (pages > LIMITS.pages) return problem(`The manual has ${pages} pages; the limit is ${LIMITS.pages}.`, 400);

    const day = new Date().toISOString().slice(0, 10);
    const visitor = request.headers.get("cf-connecting-ip") || "unknown";
    const count = (who) => this.sql.exec("SELECT n FROM counts WHERE day = ? AND visitor = ?", day, who).toArray()[0]?.n || 0;
    const waiting = this.sql.exec("SELECT COUNT(*) AS n FROM jobs WHERE state = 'queued'").one().n;
    if (waiting >= LIMITS.queued) return problem("The queue is full right now. Try again in a few minutes.", 429);
    if (count("*") >= LIMITS.daily) return problem("Today's free videos have all been made. Come back tomorrow, or watch the examples above.", 429);
    if (count(visitor) >= LIMITS.per_visitor) return problem(`You can make ${LIMITS.per_visitor} videos a day. Come back tomorrow.`, 429);

    const id = crypto.randomUUID().replaceAll("-", "").slice(0, 12);
    const seq = (this.sql.exec("SELECT MAX(seq) AS m FROM jobs").one().m || 0) + 1;
    this.ctx.storage.transactionSync(() => {
      this.sql.exec("INSERT INTO jobs (id, seq, state, created, touched) VALUES (?, ?, 'queued', ?, ?)", id, seq, now(), now());
      this.putBlob(id, "pdf", bytes);
      for (const who of ["*", visitor]) {
        this.sql.exec(
          "INSERT INTO counts (day, visitor, n) VALUES (?, ?, 1) ON CONFLICT (day, visitor) DO UPDATE SET n = n + 1", day, who);
      }
    });
    return json(this.status(id));
  }

  status(id) {
    const job = this.sql.exec("SELECT * FROM jobs WHERE id = ?", id).toArray()[0];
    if (!job) return null;
    const position = job.state === "queued"
      ? this.sql.exec("SELECT COUNT(*) AS n FROM jobs WHERE state IN ('queued', 'running') AND seq < ?", job.seq).one().n
      : 0;
    return { id, state: job.state, position, phase: job.phase, phases: PHASES, title: job.title, message: job.message };
  }

  statusResponse(id) {
    const status = this.status(id);
    return status ? json(status) : problem("This video has expired. Upload the manual again.", 404);
  }

  video(id) {
    const job = this.status(id);
    if (!job || job.state !== "done") return problem("The video isn't ready yet.", 404);
    const name = (job.title || "assembly").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
    return withRange(this.request, this.getBlob(id, "video"), {
      "content-type": "video/mp4",
      "content-disposition": `inline; filename="${name}_assembly.mp4"`,
      "cache-control": "private, max-age=3600",
    });
  }

  // ---------- the render machine ----------

  authorised(request) {
    const secret = this.env.WORKER_SECRET || "";
    const given = (request.headers.get("authorization") || "").replace(/^Bearer /, "");
    if (!secret || given.length !== secret.length) return false;
    let diff = 0;
    for (let i = 0; i < secret.length; i++) diff |= secret.charCodeAt(i) ^ given.charCodeAt(i);
    return diff === 0;
  }

  async workerRoute(parts, method, request) {
    // POST poll: the next queued job, now running, or 204 when there is none.
    if (method === "POST" && parts[0] === "poll") {
      const job = this.sql.exec("SELECT id FROM jobs WHERE state = 'queued' ORDER BY seq LIMIT 1").toArray()[0];
      if (!job) return new Response(null, { status: 204 });
      this.sql.exec("UPDATE jobs SET state = 'running', phase = 0, touched = ? WHERE id = ?", now(), job.id);
      return json({ id: job.id });
    }
    if (method === "POST" && parts[0] === "heartbeat") {
      this.sql.exec("UPDATE jobs SET touched = ? WHERE state = 'running'", now());
      return new Response(null, { status: 204 });
    }

    const [, id, action] = parts; // jobs/<id>/<action>
    if (parts[0] !== "jobs" || !id) return problem("Not found.", 404);
    const job = this.sql.exec("SELECT state FROM jobs WHERE id = ?", id).toArray()[0];
    if (!job) return problem("Not found.", 404);

    if (method === "GET" && action === "pdf") {
      return new Response(this.getBlob(id, "pdf"), { headers: { "content-type": "application/pdf" } });
    }
    if (job.state !== "running") return problem("This job isn't running.", 409);

    if (method === "POST" && action === "phase") {
      const { phase } = await request.json();
      this.sql.exec("UPDATE jobs SET phase = ?, touched = ? WHERE id = ?",
        Math.max(0, Math.min(PHASES.length - 1, phase | 0)), now(), id);
      return new Response(null, { status: 204 });
    }
    if (method === "POST" && action === "done") {
      const bytes = new Uint8Array(await request.arrayBuffer());
      const title = decodeURIComponent(request.headers.get("x-title") || "").slice(0, 120);
      this.ctx.storage.transactionSync(() => {
        this.putBlob(id, "video", bytes);
        this.sql.exec("DELETE FROM blobs WHERE job = ? AND kind = 'pdf'", id);
        this.sql.exec("UPDATE jobs SET state = 'done', phase = ?, title = ?, finished = ? WHERE id = ?",
          PHASES.length - 1, title, now(), id);
      });
      return new Response(null, { status: 204 });
    }
    if (method === "POST" && action === "failed") {
      const { message } = await request.json();
      this.finishFailed(id, String(message || FAILED_BUILDING).slice(0, 200));
      return new Response(null, { status: 204 });
    }
    return problem("Not found.", 404);
  }

  // ---------- storage ----------

  putBlob(job, kind, bytes) {
    this.sql.exec("DELETE FROM blobs WHERE job = ? AND kind = ?", job, kind);
    for (let part = 0, at = 0; at < bytes.length || part === 0; part++, at += CHUNK) {
      this.sql.exec("INSERT INTO blobs (job, kind, part, data) VALUES (?, ?, ?, ?)",
        job, kind, part, bytes.slice(at, at + CHUNK));
    }
  }

  getBlob(job, kind) {
    const chunks = this.sql.exec("SELECT data FROM blobs WHERE job = ? AND kind = ? ORDER BY part", job, kind)
      .toArray().map((row) => new Uint8Array(row.data));
    const out = new Uint8Array(chunks.reduce((n, c) => n + c.length, 0));
    let at = 0;
    for (const chunk of chunks) { out.set(chunk, at); at += chunk.length; }
    return out;
  }

  finishFailed(id, message) {
    this.sql.exec("DELETE FROM blobs WHERE job = ? AND kind = 'pdf'", id);
    this.sql.exec("UPDATE jobs SET state = 'failed', message = ?, finished = ? WHERE id = ?", message, now(), id);
  }

  // Fail jobs the render machine lost, and delete finished ones after an hour.
  tidy() {
    const t = now();
    for (const { id } of this.sql.exec(
      "SELECT id FROM jobs WHERE state = 'running' AND touched < ?", t - RUNNING_LOST_SECONDS).toArray()) {
      this.finishFailed(id, FAILED_BUILDING);
    }
    if (!this.online()) {
      for (const { id } of this.sql.exec(
        "SELECT id FROM jobs WHERE state = 'queued' AND created < ?", t - QUEUED_LOST_SECONDS).toArray()) {
        this.finishFailed(id, OFFLINE);
      }
    }
    for (const { id } of this.sql.exec(
      "SELECT id FROM jobs WHERE finished IS NOT NULL AND finished < ?", t - LIMITS.keep_seconds).toArray()) {
      this.sql.exec("DELETE FROM blobs WHERE job = ?", id);
      this.sql.exec("DELETE FROM jobs WHERE id = ?", id);
    }
  }
}
