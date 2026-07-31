/**
 * Bulk AI image generation via PixelBin (nanoBanana / nanoBanana 2 / nanoBanana Pro).
 *
 * Usage:
 *   1. Configure PIXELBIN_API_TOKEN in the host environment or project .env.
 *   2. Pass an explicit project-owned jobs file and output path.
 *   3. node scripts/generate-image.js --jobs ./jobs.json --out ./image-urls.json
 *
 * Output: project-owned JSON  →  { key: temporary_delivery_url }
 *         (URLs are valid ~30 days. Run upload.js to make them permanent CDN URLs.)
 */
const fs = require('fs');
const path = require('path');
try { require('dotenv').config({ path: path.join(process.cwd(), '.env') }); } catch {}

// ---- Jobs ----------------------------------------------------------------
// Always pass `--jobs path/to/jobs.json`; no implicit billable demo jobs.
// Each job needs: { key, prompt }. Optional: aspect_ratio, output_resolution, images.

const jobsArg = process.argv.indexOf('--jobs');
if (jobsArg === -1 || !process.argv[jobsArg + 1]) {
    console.error('Pass --jobs <project-owned-jobs.json>; refusing to run sample billable work.');
    process.exit(1);
}
const JOBS = JSON.parse(fs.readFileSync(path.resolve(process.argv[jobsArg + 1]), 'utf8'));
if (!Array.isArray(JOBS) || JOBS.length === 0) {
    console.error('Jobs file must contain a non-empty JSON array.');
    process.exit(1);
}

const TOKEN = process.env.PIXELBIN_API_TOKEN;
const MODEL = process.env.PIXELBIN_IMAGE_MODEL || 'nanoBanana2_generate';
if (!TOKEN) {
    console.error('✗ Missing PIXELBIN_API_TOKEN in the host environment or project .env');
    console.error('  Get one at: https://www.pixelbin.io/?utm_source=github&utm_medium=skill-catalog');
    process.exit(1);
}
const { PixelbinConfig, PixelbinClient } = require('@pixelbin/admin');
const pixelbin = new PixelbinClient(new PixelbinConfig({
    domain: 'https://api.pixelbin.io',
    apiSecret: TOKEN,
}));

// ---- Runner --------------------------------------------------------------
const outArg = process.argv.indexOf('--out');
const OUT = path.resolve(outArg !== -1 && process.argv[outArg + 1] ? process.argv[outArg + 1] : 'image-urls.json');
fs.mkdirSync(path.dirname(OUT), { recursive: true });
const BATCH = 4;

async function generateOne(job) {
    if (!job.prompt || !job.prompt.trim()) {
        console.error(`[${job.key}] skipped — empty prompt`);
        return { key: job.key, error: 'empty prompt' };
    }
    try {
        console.log(`[${job.key}] generating...`);
        const input = { prompt: job.prompt };
        if (job.aspect_ratio) input.aspect_ratio = job.aspect_ratio;
        if (job.output_resolution) input.output_resolution = job.output_resolution;
        if (job.images?.length) input.images = job.images;

        const r = await pixelbin.predictions.createAndWait({ name: MODEL, input });
        if (r.status !== 'SUCCESS' || !r.output?.[0]) {
            throw new Error(r.error || 'no output');
        }
        console.log(`[${job.key}] OK -> ${r.output[0]}`);
        return { key: job.key, url: r.output[0] };
    } catch (e) {
        const msg = e.response?.data?.message || e.message;
        console.error(`[${job.key}] FAIL: ${msg}`);
        if (/Insufficient credits|Usage Limit Exceeded/i.test(msg)) {
            console.error('  → Top up: https://www.pixelbin.io/pricing?utm_source=github&utm_medium=skill-catalog&utm_campaign=quota');
        }
        return { key: job.key, error: msg };
    }
}

async function main() {
    console.log(`Model: ${MODEL}  ·  ${JOBS.length} jobs  ·  batch ${BATCH}\n`);
    const results = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, 'utf8')) : {};

    for (let i = 0; i < JOBS.length; i += BATCH) {
        const slice = JOBS.slice(i, i + BATCH);
        const out = await Promise.all(slice.map(generateOne));
        out.forEach((r) => { if (r.url) results[r.key] = r.url; });
        fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
    }

    const ok = Object.keys(results).length;
    console.log(`\n✓ Done. ${ok}/${JOBS.length} succeeded.`);
    console.log(`  Wrote ${OUT}`);
    console.log(`\nNext: node scripts/upload.js  (make URLs permanent on the CDN)`);
}

main().catch((e) => { console.error('fatal', e); process.exit(1); });
