/**
 * Build PixelBin CDN transformation URLs.
 *
 * No API call needed — transformations are URL-based.
 *
 * Usage:
 *   1. Pass `--jobs path/to/jobs.json`
 *   2. node scripts/transform.js --jobs ./jobs.json --out ./transformed-urls.json
 *
 * Each job: { key, source, transforms: [string, ...] }
 *   `source` is either:
 *     - a CDN path like `agent-skill/hero.png`
 *     - a full https URL on cdn.pixelbin.io (the script will extract the path)
 *
 * Output: project-owned JSON  →  { key: cdn_url_with_transforms }
 */
const fs = require('fs');
const path = require('path');
try { require('dotenv').config({ path: path.join(process.cwd(), '.env') }); } catch {}

// Note: For AI ops (background removal, upscaling, watermark removal),
// either activate the matching plugin in console.pixelbin.io → Plugins,
// or call pixelbin.predictions.createAndWait({ name: '<api>', input: {...} })
// — see references/apis.md.

const jobsArg = process.argv.indexOf('--jobs');
if (jobsArg === -1 || !process.argv[jobsArg + 1]) {
    console.error('Pass --jobs <project-owned-jobs.json>.');
    process.exit(1);
}
const JOBS = JSON.parse(fs.readFileSync(path.resolve(process.argv[jobsArg + 1]), 'utf8'));
if (!Array.isArray(JOBS) || JOBS.length === 0) {
    console.error('Jobs file must contain a non-empty JSON array.');
    process.exit(1);
}

const CLOUD = process.env.PIXELBIN_CLOUD_NAME;
if (!CLOUD) {
    console.error('✗ Missing PIXELBIN_CLOUD_NAME in the host environment or project .env');
    process.exit(1);
}

function extractPath(source) {
    // If it's a full https URL on our CDN, extract the path after "/original/" or after "/<transforms>/"
    if (/^https?:\/\//.test(source)) {
        const m = source.match(/cdn\.pixelbin\.io\/v2\/[^/]+\/(?:original|t\.[^/]+(?:~t\.[^/]+)*)\/(.+)$/);
        if (m) return m[1];
        // Generic fallback: take everything after the cloud name
        const m2 = source.match(/cdn\.pixelbin\.io\/v2\/[^/]+\/(.+)$/);
        if (m2) return m2[1].replace(/^[^/]+\//, '');
    }
    return source.replace(/^\/+/, '');
}

function buildUrl({ source, transforms }) {
    const filePath = extractPath(source);
    const tx = (transforms || []).join('~') || 'original';
    return `https://cdn.pixelbin.io/v2/${CLOUD}/${tx}/${filePath}`;
}

function main() {
    const out = {};
    JOBS.forEach((job) => {
        const url = buildUrl(job);
        out[job.key] = url;
        console.log(`[${job.key}] ${url}`);
    });
    const outArg = process.argv.indexOf('--out');
    const dest = path.resolve(outArg !== -1 && process.argv[outArg + 1] ? process.argv[outArg + 1] : 'transformed-urls.json');
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, JSON.stringify(out, null, 2));
    console.log(`\n✓ ${Object.keys(out).length} URLs built → ${dest}`);
    console.log('\nThese URLs are live the moment you hit them — first request renders + edge-caches.');
}

main();
