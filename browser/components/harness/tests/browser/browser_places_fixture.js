/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// Generator for a realistic-but-entirely-synthetic places.sqlite fixture
// (tests/fixtures/places-fixture.sqlite). All URLs, titles and timestamps
// come from the embedded public-information lists below and a seeded PRNG:
// nothing is derived from any real profile. Inserting through
// PlacesUtils.history means guids, url_hash, frecency and moz_origins are
// all computed by the real Places code.
//
// The checked-in fixture is regenerated with:
//   MOZ_GENERATE_PLACES_FIXTURE=$PWD/browser/components/harness/tests/fixtures/places-fixture.sqlite \
//     ./mach mochitest --headless browser/components/harness/tests/browser/browser_places_fixture.js
// Without the env var this test runs a small generation to keep the
// generator itself covered.

const { PlacesUtils } = ChromeUtils.importESModule(
  "resource://gre/modules/PlacesUtils.sys.mjs"
);

// Deterministic PRNG (mulberry32).
function makeRandom(seed) {
  let state = seed;
  return () => {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const WIKI_TOPICS = [
  "Rayleigh_scattering", "SQLite", "Firefox", "WebAssembly", "Rust_(programming_language)",
  "JavaScript", "Prime_gap", "Alan_Turing", "Ada_Lovelace", "Antikythera_mechanism",
  "Great_Barrier_Reef", "Coffee", "Sourdough", "Fermentation", "Mount_Rainier",
  "Aurora_borealis", "Monarch_butterfly", "Baroque_music", "Johann_Sebastian_Bach",
  "Impressionism", "Golden_Gate_Bridge", "Transistor", "Moore's_law", "Photosynthesis",
  "Plate_tectonics", "Voyager_1", "James_Webb_Space_Telescope", "Byzantine_Empire",
  "Silk_Road", "Printing_press", "Public-key_cryptography", "Diffie-Hellman_key_exchange",
  "Bicycle", "Espresso", "Cast_iron_cookware", "Knot_theory", "Origami",
  "Redwood_National_and_State_Parks", "Tide_pool", "Octopus", "Corvidae",
  "Type_system", "Garbage_collection_(computer_science)", "Virtual_machine",
  "Hypervisor", "Unix", "History_of_the_Internet", "HTTP", "Transport_Layer_Security",
  "Same-origin_policy", "Content_Security_Policy",
];

const GITHUB_REPOS = [
  "mozilla-firefox/firefox", "sqlite/sqlite", "oven-sh/bun", "denoland/deno",
  "rust-lang/rust", "nodejs/node", "microsoft/vscode", "python/cpython",
  "torvalds/linux", "containers/libkrun", "astral-sh/uv", "d3/d3",
  "sql-js/sql.js", "w3c/csswg-drafts", "whatwg/html", "tc39/ecma262",
];

const SO_SLUGS = [
  "how-do-i-undo-the-most-recent-local-commits-in-git",
  "what-is-the-difference-between-let-and-var",
  "how-to-check-if-a-file-exists-in-bash",
  "why-is-processing-a-sorted-array-faster",
  "how-do-i-iterate-over-a-map-in-javascript",
  "sqlite-vs-postgres-for-a-small-app",
  "how-to-profile-a-slow-sql-query",
  "css-grid-vs-flexbox-when-to-use-which",
  "async-await-vs-promises-in-javascript",
  "how-to-parse-json-in-a-shell-script",
];

const MDN_PATHS = [
  "Web/API/IndexedDB_API", "Web/API/Web_Workers_API", "Web/API/Fetch_API",
  "Web/JavaScript/Reference/Global_Objects/Array", "Web/CSS/CSS_grid_layout",
  "Web/CSS/flexbox", "Web/API/WebAssembly", "Web/HTTP/CSP",
  "Web/API/Canvas_API", "Web/JavaScript/Guide/Modules",
  "Web/API/URL_Pattern_API", "Web/CSS/color_value",
];

const SEARCH_QUERIES = [
  "best sourdough starter schedule", "sqlite vacuum into", "bun sqlite example",
  "css grid center div", "flights sfo to yyz", "weather this weekend",
  "d3 bar chart tutorial", "wasm memory limits", "prime gaps visualization",
  "firefox about config tips", "espresso grind size chart", "hiking near tacoma",
  "javascript structuredclone", "indexeddb quota", "git rebase interactive",
  "rust borrow checker explained", "national park reservations",
];

const YT_TITLES = [
  "Building a Database From Scratch", "The Art of Sourdough", "How CPUs Work",
  "A Tour of the Solar System", "Understanding WebAssembly", "Baroque Masterpieces",
  "Bike Maintenance Basics", "The History of Unix", "Fermentation for Beginners",
  "Watchmaking Up Close",
];

const NEWS_SITES = ["www.nytimes.com", "www.bbc.com", "www.theguardian.com", "arstechnica.com"];
const NEWS_SECTIONS = ["technology", "science", "climate", "business", "culture"];
const NEWS_SLUGS = [
  "chip-makers-race-to-smaller-nodes", "ocean-currents-shift-study-finds",
  "the-quiet-rise-of-local-first-software", "why-everyone-is-baking-again",
  "electric-grid-storage-milestone", "new-telescope-images-released",
  "open-source-funding-models-mature", "city-bike-lanes-expand",
];

// Weighted domain mix: [weight, generator(random) -> {url, title}].
function makeGenerators(random) {
  const pick = list => list[Math.floor(random() * list.length)];
  const id = max => Math.floor(random() * max);
  return [
    [18, () => {
      const topic = pick(WIKI_TOPICS);
      return {
        url: `https://en.wikipedia.org/wiki/${topic}`,
        title: `${topic.replaceAll("_", " ")} - Wikipedia`,
      };
    }],
    [14, () => {
      const repo = pick(GITHUB_REPOS);
      const kind = random();
      if (kind < 0.4) {
        return { url: `https://github.com/${repo}`, title: `GitHub - ${repo}` };
      }
      if (kind < 0.7) {
        const n = 1 + id(9000);
        return { url: `https://github.com/${repo}/issues/${n}`, title: `Issue #${n} - ${repo}` };
      }
      const n = 1 + id(9000);
      return { url: `https://github.com/${repo}/pull/${n}`, title: `Pull request #${n} - ${repo}` };
    }],
    [12, () => {
      const q = pick(SEARCH_QUERIES);
      return {
        url: `https://www.google.com/search?q=${encodeURIComponent(q)}`,
        title: `${q} - Google Search`,
      };
    }],
    [10, () => {
      const slug = pick(SO_SLUGS);
      return {
        url: `https://stackoverflow.com/questions/${100000 + id(9000000)}/${slug}`,
        title: `${slug.replaceAll("-", " ")} - Stack Overflow`,
      };
    }],
    [9, () => {
      const path = pick(MDN_PATHS);
      return {
        url: `https://developer.mozilla.org/en-US/docs/${path}`,
        title: `${path.split("/").pop().replaceAll("_", " ")} | MDN`,
      };
    }],
    [8, () => {
      const site = pick(NEWS_SITES);
      const section = pick(NEWS_SECTIONS);
      const slug = pick(NEWS_SLUGS);
      return {
        url: `https://${site}/${section}/${slug}`,
        title: slug.replaceAll("-", " "),
      };
    }],
    [7, () => {
      const title = pick(YT_TITLES);
      const vid = Array.from({ length: 11 }, () =>
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"[id(64)]
      ).join("");
      return { url: `https://www.youtube.com/watch?v=${vid}`, title: `${title} - YouTube` };
    }],
    [6, () => {
      return {
        url: `https://news.ycombinator.com/item?id=${30000000 + id(15000000)}`,
        title: "Hacker News",
      };
    }],
    [5, () => {
      const sub = pick(["programming", "firefox", "webdev", "sourdough", "AskHistorians"]);
      const slug = pick(SO_SLUGS).slice(0, 24);
      return {
        url: `https://www.reddit.com/r/${sub}/comments/${id(9999999).toString(36)}/${slug}/`,
        title: `${slug.replaceAll("-", " ")} : r/${sub}`,
      };
    }],
    [5, () => {
      const page = pick(["bun.sh/docs/api/sqlite", "react.dev/learn", "nodejs.org/api/fs.html",
        "docs.python.org/3/library/sqlite3.html", "sqlite.org/lang_vacuum.html",
        "sqlite.org/wal.html", "docs.astral.sh/uv/"]);
      return { url: `https://${page}`, title: page.split("/").pop() || page };
    }],
  ];
}

async function generate({ sessions, seed, outPath }) {
  const random = makeRandom(seed);
  const generators = makeGenerators(random);
  const totalWeight = generators.reduce((sum, [w]) => sum + w, 0);
  const pickPage = () => {
    let roll = random() * totalWeight;
    for (const [weight, gen] of generators) {
      roll -= weight;
      if (roll <= 0) {
        return gen();
      }
    }
    return generators[0][1]();
  };

  await PlacesUtils.history.clear();

  // Fixed reference date so output is deterministic for a given seed.
  const END = Date.UTC(2026, 5, 30, 12, 0, 0);
  const DAY = 24 * 60 * 60 * 1000;
  const T = PlacesUtils.history.TRANSITIONS;

  // Revisit pool: popular pages accumulate visit_count like real browsing.
  const pool = [];
  const pages = new Map();
  let visitCount = 0;
  for (let s = 0; s < sessions; s++) {
    // Weekday-weighted day in the last year, diurnal hour curve.
    let day;
    do {
      day = Math.floor(random() * 365);
    } while ([0, 6].includes(new Date(END - day * DAY).getUTCDay()) && random() < 0.5);
    const hourRoll = random();
    const hour =
      hourRoll < 0.45 ? 9 + Math.floor(random() * 4)
      : hourRoll < 0.8 ? 14 + Math.floor(random() * 5)
      : 20 + Math.floor(random() * 3);
    let when = END - day * DAY + (hour * 60 + Math.floor(random() * 60)) * 60 * 1000;

    const length = 2 + Math.floor(random() * 10);
    let previousUrl = null;
    for (let i = 0; i < length; i++) {
      const revisit = pool.length > 50 && random() < 0.35;
      const page = revisit ? pool[Math.floor(random() * pool.length)] : pickPage();
      if (!revisit) {
        pool.push(page);
      }
      const transition =
        i == 0
          ? random() < 0.4 ? T.TYPED : T.LINK
          : random() < 0.05 ? T.RELOAD : T.LINK;
      const record = pages.get(page.url) ?? { title: page.title, visits: [] };
      record.visits.push({
        date: new Date(when),
        transition,
        referrer: i > 0 && previousUrl && previousUrl != page.url ? previousUrl : undefined,
      });
      pages.set(page.url, record);
      previousUrl = page.url;
      when += (5 + Math.floor(random() * 180)) * 1000;
      visitCount++;
    }
  }

  const entries = [...pages.entries()].map(([url, { title, visits }]) => ({
    url,
    title,
    visits,
  }));
  for (let i = 0; i < entries.length; i += 300) {
    await PlacesUtils.history.insertMany(entries.slice(i, i + 300));
  }

  await PlacesUtils.bookmarks.insertTree({
    guid: PlacesUtils.bookmarks.toolbarGuid,
    children: [
      { title: "MDN", url: "https://developer.mozilla.org/" },
      { title: "GitHub", url: "https://github.com/" },
      { title: "HN", url: "https://news.ycombinator.com/" },
      {
        title: "Reference",
        type: PlacesUtils.bookmarks.TYPE_FOLDER,
        children: [
          { title: "SQLite docs", url: "https://sqlite.org/docs.html" },
          { title: "bun:sqlite", url: "https://bun.sh/docs/api/sqlite" },
          { title: "uv", url: "https://docs.astral.sh/uv/" },
          { title: "CSS Grid | MDN", url: "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout" },
        ],
      },
      {
        title: "Reading",
        type: PlacesUtils.bookmarks.TYPE_FOLDER,
        children: WIKI_TOPICS.slice(0, 8).map(topic => ({
          title: `${topic.replaceAll("_", " ")} - Wikipedia`,
          url: `https://en.wikipedia.org/wiki/${topic}`,
        })),
      },
    ],
  });

  if (outPath) {
    await IOUtils.remove(outPath, { ignoreAbsent: true });
    await PlacesUtils.withConnectionWrapper("fixture-vacuum", conn =>
      conn.execute(`VACUUM INTO '${outPath.replaceAll("'", "''")}'`)
    );
  }
  return { pages: pages.size, visits: visitCount };
}

add_task(async function test_places_fixture_generator() {
  const outPath = Services.env.get("MOZ_GENERATE_PLACES_FIXTURE") || null;
  const full = !!outPath;
  const stats = await generate({
    sessions: full ? 3500 : 60,
    seed: 20260728,
    outPath,
  });
  info(`generated ${stats.pages} pages / ${stats.visits} visits`);
  Assert.greater(stats.pages, full ? 3000 : 50, "plausible page count");
  const inserted = await PlacesUtils.withConnectionWrapper("fixture-check", c =>
    c.execute("SELECT COUNT(*) AS c FROM moz_places WHERE url_hash != 0")
  );
  Assert.greater(
    inserted[0].getResultByName("c"),
    0,
    "places rows carry real url_hash values"
  );
  if (outPath) {
    const size = (await IOUtils.stat(outPath)).size;
    info(`fixture written to ${outPath} (${(size / 1024 / 1024).toFixed(1)} MB)`);
    ok(size > 0, "fixture file written");
  }
});
