// AI Assembly Video Generator: the showcase studio (manual pages and parts list kept
// in step with the video) and "try your own manual" uploads.
"use strict";

const $ = (id) => document.getElementById(id);
const SHOWCASE = "showcase/";
const POLL_MS = 2000;
const LIMITS_MS = 30000;

const state = {
  entries: [],      // [{name, title, data}]
  current: null,    // the entry in the studio
  stepIndex: -1,
  page: 1,
};

// ---------- helpers ----------

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value);
  }
  for (const child of children) {
    if (child != null) node.append(child instanceof Node ? child : document.createTextNode(child));
  }
  return node;
}

function clock(seconds) {
  const s = Math.max(0, Math.round(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

// Steps of the build, without the closing "Assembly complete" caption.
const buildSteps = (data) => data.steps.filter((s) => s.label.startsWith("Step"));

// The number in a step's circle: from its label ("Step 3 of 8"), or a tick
// for the closing captions.
const stepNumber = (step) => (step.label.match(/^Step (\d+)/) || [, "✓"])[1];

const tickSvg = () => {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 12 12");
  svg.innerHTML = '<path d="M2 6.5 L5 9 L10 3" />';
  return svg;
};

// ---------- loading ----------

async function loadShowcase() {
  const list = await (await fetch(SHOWCASE + "showcase.json")).json();
  const entries = await Promise.all(list.map(async (entry) => {
    try {
      const data = await (await fetch(`${SHOWCASE}${entry.name}/data.json`)).json();
      return { ...entry, data };
    } catch {
      return null;
    }
  }));
  return entries.filter(Boolean);
}

function showStats(entries) {
  const steps = entries.reduce((n, e) => n + buildSteps(e.data).length, 0);
  const pages = entries.reduce((n, e) => n + e.data.pages.length, 0);
  const parts = entries.reduce((n, e) => n + e.data.parts.reduce((m, p) => m + p.quantity, 0), 0);
  const stats = [
    [entries.length, "pieces of furniture"],
    [pages, "manual pages read"],
    [steps, "steps animated"],
    [parts, "parts & fittings placed"],
  ];
  $("stats").replaceChildren(...stats.map(([n, label]) => el("div", {}, el("dt", {}, String(n)), el("dd", {}, label))));
}

function showHero(entry) {
  const base = `${SHOWCASE}${entry.name}/`;
  const firstStepPage = buildSteps(entry.data).find((s) => s.pages.length)?.pages[0] || 1;
  $("hero-page").src = base + "pages/" + entry.data.pages[firstStepPage - 1];
  const video = $("hero-video");
  video.src = base + "video.mp4";
  video.poster = base + "poster.jpg";
  video.play().catch(() => {});
}

// ---------- cards ----------

function showCards(entries) {
  const cards = entries.map((entry, i) => {
    const base = `${SHOWCASE}${entry.name}/`;
    const video = el("video", { muted: "", loop: "", playsinline: "", preload: "none" });
    video.muted = true;
    const card = el("button", { class: "card", type: "button", "data-name": entry.name },
      el("div", { class: "card-media" },
        el("img", { src: base + "poster.jpg", alt: "", loading: "lazy" }),
        video,
        el("span", { class: "card-badge" }, String(i + 1).padStart(2, "0")),
      ),
      el("div", { class: "card-body" },
        el("div", { class: "card-title" }, entry.title),
        el("div", { class: "card-meta mono" },
          el("span", {}, `${buildSteps(entry.data).length} steps`),
          el("span", {}, `${entry.data.pages.length} pages`),
          el("span", {}, clock(entry.data.duration)),
        ),
      ),
    );
    card.addEventListener("mouseenter", () => {
      if (!video.src) {
        video.src = base + "video.mp4";
        video.addEventListener("playing", () => video.classList.add("ready"), { once: true });
      }
      video.currentTime = Math.max(0, entry.data.steps[0]?.start || 0);
      video.play().catch(() => {});
    });
    card.addEventListener("mouseleave", () => video.pause());
    card.addEventListener("click", () => {
      openInStudio(entry, true);
      $("watch").scrollIntoView({ behavior: "smooth" });
    });
    return card;
  });
  $("cards").replaceChildren(...cards);
}

// ---------- studio ----------

function openInStudio(entry, autoplay) {
  state.current = entry;
  state.stepIndex = -1;
  const { data } = entry;
  const base = `${SHOWCASE}${entry.name}/`;

  document.querySelectorAll(".card").forEach((c) => c.classList.toggle("active", c.dataset.name === entry.name));
  $("studio-title").textContent = entry.title;
  $("studio-meta").textContent = `${buildSteps(data).length} steps · ${data.pages.length}-page manual · ${clock(data.duration)}`;

  const video = $("video");
  video.src = base + "video.mp4";
  video.poster = base + "poster.jpg";
  if (autoplay) video.play().catch(() => {});

  // Preload the manual's pages so they turn without a flash.
  data.pages.forEach((file) => { new Image().src = base + "pages/" + file; });

  $("timeline").replaceChildren(...data.steps.map((step, i) =>
    el("button", {
      type: "button", role: "listitem",
      title: `${step.label}: ${step.caption}`,
      "aria-label": `${step.label}: ${step.caption}`,
      onclick: () => seekStep(i),
    })));

  $("steps").replaceChildren(...data.steps.map((step, i) =>
    el("li", { onclick: () => seekStep(i) },
      el("span", { class: "step-dot" }, stepNumber(step)),
      el("span", {}, step.caption),
      el("span", { class: "t mono muted" }, clock(step.start)),
    )));

  $("parts").replaceChildren(...data.parts.map((part) =>
    el("li", {},
      el("span", { class: "tick" }, tickSvg()),
      el("span", { class: "qty" }, `${part.quantity}x`),
      el("span", { class: "name" }, part.name),
      part.hardware ? el("span", { class: "hw" }, "fitting") : null,
    )));

  const first = buildSteps(data).find((s) => s.pages.length);
  setPage(first ? first.pages[0] : 1, false);
  update(0);
}

function stepAt(t) {
  const steps = state.current.data.steps;
  let index = -1;
  steps.forEach((step, i) => { if (t >= step.start - 0.05) index = i; });
  return index;
}

function update(t) {
  if (!state.current) return;
  const { data } = state.current;
  const index = stepAt(t);
  if (index === state.stepIndex) return;
  state.stepIndex = index;

  const timeline = $("timeline").children;
  const steps = $("steps").children;
  for (let i = 0; i < data.steps.length; i++) {
    const done = i < index, current = i === index;
    timeline[i].classList.toggle("done", done);
    timeline[i].classList.toggle("current", current);
    steps[i].classList.toggle("done", done);
    steps[i].classList.toggle("current", current);
  }

  const step = data.steps[Math.max(index, 0)];
  const total = buildSteps(data).length;
  $("now-num").textContent = index < 0 ? "0" : stepNumber(step);
  $("now-label").textContent = index < 0 ? `${total} steps` : step.label;
  $("now-caption").textContent = index < 0 ? "Press play: the parts come in one step at a time." : step.caption;

  // Parts: used in an earlier step, or in this one.
  const used = new Set(), now = new Set(index >= 0 ? data.steps[index].parts : []);
  data.steps.slice(0, Math.max(index, 0)).forEach((s) => s.parts.forEach((p) => used.add(p)));
  if (index >= 0 && !data.steps[index].label.startsWith("Step")) data.parts.forEach((_, p) => used.add(p));
  const parts = $("parts").children;
  for (let p = 0; p < parts.length; p++) {
    parts[p].classList.toggle("used", used.has(p));
    parts[p].classList.toggle("now", now.has(p) && !used.has(p));
  }
  $("parts-progress").textContent = `${used.size} / ${data.parts.length}`;
  const firstNow = [...now].find((p) => !used.has(p));
  if (firstNow != null) scrollIntoList($("parts"), parts[firstNow]);
  if (index >= 0) scrollIntoList($("steps"), steps[index]);

  if ($("follow").checked && index >= 0 && step.pages.length) setPage(step.pages[0], true);
}

// Scroll a list (not the page) so the item is in view.
function scrollIntoList(list, item) {
  const top = item.offsetTop - list.offsetTop;
  if (top < list.scrollTop || top + item.offsetHeight > list.scrollTop + list.clientHeight) {
    list.scrollTo({ top: top - list.clientHeight / 3, behavior: "smooth" });
  }
}

function setPage(page, animate) {
  const { data, name } = state.current;
  page = Math.min(Math.max(1, page), data.pages.length);
  if (page === state.page && $("manual-img").getAttribute("src")) return;
  state.page = page;
  const img = $("manual-img");
  img.src = `${SHOWCASE}${name}/pages/${data.pages[page - 1]}`;
  img.alt = `${state.current.title} manual, page ${page}`;
  if (animate) {
    img.classList.remove("flip");
    void img.offsetWidth;
    img.classList.add("flip");
  }
  $("page-tag").textContent = `p. ${page}`;
  $("page-count").textContent = `${page} / ${data.pages.length}`;
  $("page-prev").disabled = page <= 1;
  $("page-next").disabled = page >= data.pages.length;
}

function seekStep(i) {
  const steps = state.current.data.steps;
  i = Math.min(Math.max(0, i), steps.length - 1);
  const video = $("video");
  video.currentTime = steps[i].start + 0.05;
  $("follow").checked = true;
  update(video.currentTime);
  video.play().catch(() => {});
}

function wireStudio() {
  const video = $("video");
  // timeupdate fires ~4 times a second; follow every frame while playing.
  const tick = () => {
    update(video.currentTime);
    if (!video.paused) requestAnimationFrame(tick);
  };
  video.addEventListener("play", () => requestAnimationFrame(tick));
  video.addEventListener("seeked", () => update(video.currentTime));
  video.addEventListener("timeupdate", () => update(video.currentTime));

  const turn = (by) => { $("follow").checked = false; setPage(state.page + by, true); };
  $("page-prev").addEventListener("click", () => turn(-1));
  $("page-next").addEventListener("click", () => turn(1));

  document.addEventListener("keydown", (e) => {
    if (!state.current || e.target.closest("input, textarea")) return;
    const studio = $("studio").getBoundingClientRect();
    if (studio.bottom < 0 || studio.top > innerHeight) return;
    if (e.key === "ArrowRight") { e.preventDefault(); seekStep(state.stepIndex + 1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); seekStep(state.stepIndex - 1); }
  });
}

// ---------- try your own ----------

const limits = { pages: 10, mb: 2 };

function showError(message) {
  $("try-error").textContent = message;
  $("try-error").hidden = !message;
}

async function upload(file) {
  showError("");
  if (!file || $("file").disabled) return;
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    return showError("That isn't a PDF. Choose the manual's PDF file.");
  }
  if (file.size > limits.mb * 1024 * 1024) {
    return showError(`The file is ${(file.size / 1024 / 1024).toFixed(1)} MB; the limit is ${limits.mb} MB.`);
  }

  $("drop").hidden = true;
  $("job").hidden = false;
  $("job").classList.remove("finished");
  $("job-result").hidden = true;
  $("job-title").textContent = `Uploading ${file.name}…`;
  $("job-sub").textContent = "";
  $("phases").replaceChildren();

  const form = new FormData();
  form.append("file", file);
  try {
    const response = await fetch("api/jobs", { method: "POST", body: form });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || "The upload didn't work. Try again.");
    follow(body.id);
  } catch (e) {
    resetTry();
    showError(e.message);
  }
}

async function follow(id) {
  let job;
  try {
    const response = await fetch(`api/jobs/${id}`);
    job = await response.json();
    if (!response.ok) throw new Error(job.detail || "This video has expired.");
  } catch (e) {
    resetTry();
    return showError(e.message);
  }

  $("phases").replaceChildren(...job.phases.map((phase, i) => {
    const status = job.state === "done" || i < job.phase ? "done" : job.state === "running" && i === job.phase ? "current" : "";
    return el("li", { class: status }, phase);
  }));

  if (job.state === "queued") {
    $("job-title").textContent = job.position ? `In the queue: ${job.position} ahead of you` : "Starting…";
    $("job-sub").textContent = "Videos are made one at a time on a small free server.";
  } else if (job.state === "running") {
    $("job-title").textContent = job.phases[job.phase] + "…";
    $("job-sub").textContent = "This usually takes a few minutes. You can keep browsing the examples.";
  } else if (job.state === "failed") {
    resetTry();
    return showError(job.message);
  }

  if (job.state === "done") {
    $("job").classList.add("finished");
    $("job-title").textContent = job.title ? `${job.title}: done` : "Your video is ready";
    $("job-sub").textContent = "";
    $("job-video").src = `api/jobs/${id}/video`;
    $("job-download").href = `api/jobs/${id}/video`;
    $("job-result").hidden = false;
    return;
  }
  setTimeout(() => follow(id), POLL_MS);
}

function resetTry() {
  $("drop").hidden = false;
  $("job").hidden = true;
  $("file").value = "";
}

function wireTry() {
  const drop = $("drop");
  $("file").addEventListener("change", (e) => upload(e.target.files[0]));
  ["dragenter", "dragover"].forEach((type) => drop.addEventListener(type, (e) => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach((type) => drop.addEventListener(type, () => drop.classList.remove("over")));
  drop.addEventListener("drop", (e) => { e.preventDefault(); upload(e.dataTransfer.files[0]); });
  $("job-again").addEventListener("click", () => { resetTry(); showError(""); });

  refreshLimits();
  setInterval(refreshLimits, LIMITS_MS);
}

// The limits, and whether the render machine is on: uploads are only open
// while it is.
async function refreshLimits() {
  let online = false;
  try {
    const l = await (await fetch("api/limits", { cache: "no-store" })).json();
    Object.assign(limits, l);
    online = Boolean(l.online);
    $("rules").textContent = `PDF · up to ${l.pages} pages · up to ${l.mb} MB`;
  } catch {}
  $("machine").className = "machine " + (online ? "online" : "offline");
  $("machine-text").textContent = online
    ? "Render machine online: uploads are open"
    : "The render machine is off right now, so uploads are closed. The examples above work any time.";
  $("drop").classList.toggle("closed", !online);
  $("file").disabled = !online;
}

// ---------- start ----------

(async function start() {
  wireStudio();
  wireTry();
  try {
    state.entries = await loadShowcase();
  } catch {
    state.entries = [];
  }
  if (!state.entries.length) {
    $("pick").hidden = $("watch").hidden = true;
    return;
  }
  showStats(state.entries);
  showHero(state.entries[0]);
  showCards(state.entries);
  openInStudio(state.entries[0], false);
})();
