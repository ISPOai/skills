/**
 * Bulk AI video generation via PixelBin (Veo 3, Sora 2, Kling 3, Hailuo, Seedance, LTX-2, Wan...).
 *
 * Usage:
 *   1. Configure PIXELBIN_API_TOKEN in the host environment or project .env.
 *   2. Pass an explicit project-owned jobs file and output path.
 *   3. node scripts/generate-video.js --jobs ./jobs.json --out ./video-urls.json
 *
 * Output: project-owned JSON  →  { key: temporary_delivery_url }
 *         (Run upload.js afterwards to make these permanent CDN URLs.)
 */
const fs = require('fs');
const path = require('path');
try { require('dotenv').config({ path: path.join(process.cwd(), '.env') }); } catch {}

// ---- Jobs ----------------------------------------------------------------
// Each job: { key, prompt }. Optional: aspect_ratio, duration, images (start/end frames).

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
const MODEL = process.env.PIXELBIN_VIDEO_MODEL || 'veo3Fast_generate';
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

const outArg = process.argv.indexOf('--out');
const OUT = path.resolve(outArg !== -1 && process.argv[outArg + 1] ? process.argv[outArg + 1] : 'video-urls.json');
fs.mkdirSync(path.dirname(OUT), { recursive: true });

async function generateOne(job) {
    if (!job.prompt || !job.prompt.trim()) {
        console.error(`[${job.key}] skipped — empty prompt`);
        return { key: job.key, error: 'empty prompt' };
    }
    try {
        console.log(`[${job.key}] generating (model=${MODEL})... — this can take 1–5 min`);
        const input = { prompt: job.prompt };
        if (job.aspect_ratio) input.aspect_ratio = job.aspect_ratio;
        if (job.duration) input.duration = job.duration;
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
    console.log(`Model: ${MODEL}  ·  ${JOBS.length} job(s)\n`);
    // Videos are heavier — run sequentially to avoid timeouts
    const results = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, 'utf8')) : {};
    for (const job of JOBS) {
        const r = await generateOne(job);
        if (r.url) {
            results[r.key] = r.url;
            fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
        }
    }
    const ok = Object.keys(results).length;
    console.log(`\n✓ Done. ${ok}/${JOBS.length} succeeded.`);
    console.log(`  Wrote ${OUT}`);
}

main().catch((e) => { console.error('fatal', e); process.exit(1); });
