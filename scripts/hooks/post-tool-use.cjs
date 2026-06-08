const { emit, getToolFilePath, readHookPayload, toPosixPath } = require("./hookUtils.cjs");

const RULES = [
  {
    test: (p) => p.includes("/src/analyzer") || p.includes("/src/fetcher") || p.includes("/src/mock_data"),
    context:
      "DOMAIN CODE EDITED. Verify: (1) full type annotations on all functions, (2) no hard-coded locations, URLs, or dates — use config.py, (3) numerical code uses explicit numpy dtypes, (4) corresponding test file updated in tests/, (5) no bare except clauses.",
  },
  {
    test: (p) => p.includes("/src/visualizer"),
    context:
      "VISUALIZER EDITED. Verify: (1) seaborn + matplotlib only — no plotly, (2) charts save to output/ as PNG (300 DPI), (3) no plt.show() in non-interactive mode, (4) axis labels include units.",
  },
  {
    test: (p) => p.includes("/src/config"),
    context:
      "CONFIG EDITED. Verify: (1) location data uses Pydantic models, (2) all values are configurable (env vars or constants), (3) no domain logic in config — data only.",
  },
];

async function main() {
  const payload = await readHookPayload();
  const f = toPosixPath(getToolFilePath(payload));
  if (!f) return;
  const m = RULES.find((r) => r.test(f));
  if (m) emit({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: m.context } });
}

main().catch((e) => {
  process.stderr.write(`[hook] post-tool-use failed: ${e.message}\n`);
  process.exitCode = 0;
});
