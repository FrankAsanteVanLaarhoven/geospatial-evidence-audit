import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const repo = process.argv[2];
if (!repo) {
  process.stderr.write('Usage: node check_upstream.mjs /path/to/gods-eye-view\n');
  process.exit(2);
}
const path = resolve(repo, 'src/layers/earthquakes/records.js');
const bytes = await readFile(path);
const blobId = createHash('sha1')
  .update('blob ' + bytes.length + '\0')
  .update(bytes)
  .digest('hex');
assert.equal(blobId, '397b4bb1c875ec9d92e028079ad0fc86aa99491f',
  'Expected the reviewed upstream module from commit 6e4da23cf7a0fa27f8fd6cf9b5a141abe331ce3c');
const { normalizeEarthquakeSnapshot } = await import(pathToFileURL(path).href);
const fixture = JSON.parse(await readFile(new URL('./usgs_snapshots.json', import.meta.url)));
const summaries = fixture.snapshots.map((snapshot) => {
  const features = snapshot.records.map((record) => ({
    type: 'Feature',
    id: record.event_id,
    geometry: { type: 'Point', coordinates: [record.lon, record.lat, record.depth_km] },
    properties: {
      mag: record.magnitude,
      magType: record.mag_type,
      time: Date.parse(record.event_time),
      updated: Date.parse(record.revision_time),
      status: record.review_status,
    },
  }));
  const visible = normalizeEarthquakeSnapshot({ type: 'FeatureCollection', features });
  assert.deepEqual(visible.map((row) => row.usgsId), ['us7000twkp']);
  assert.equal(visible[0].mag, 4.3);
  assert.equal(visible.some((row) => row.usgsId === 'ci41359359'), false);
  return { published: snapshot.feed_generated_utc, ingested: features.length,
    visible_ids: visible.map((row) => row.usgsId) };
});
console.log(JSON.stringify({ upstream_blob: blobId, snapshots: summaries }, null, 2));
