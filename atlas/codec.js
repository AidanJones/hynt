export function unpackRing(value, scale) {
  const deltas = Array.isArray(value) ? value : value.d;
  const points = []; let x = 0, y = 0;
  for (let index = 0; index < deltas.length; index += 2) {
    x += deltas[index]; y += deltas[index + 1]; points.push([x / scale,y / scale]);
  }
  if (!Array.isArray(value)) for (const [index,ex,ey] of value.e) points[index] = [ex,ey];
  return points;
}
export function unpackCollection(packed) {
  if (packed.type === 'FeatureCollection') return packed;
  if (packed.format !== 'hynt-polities-1' || packed.scale !== 10000) throw new Error('Unsupported polity package format');
  const geometries = packed.geometries.map(g => {
    const polygons = g.coordinates.map(p => p.map(r => unpackRing(r,packed.scale)));
    return {type:g.type, coordinates:g.type === 'MultiPolygon' ? polygons : polygons[0]};
  });
  return {type:'FeatureCollection',features:packed.rows.map(([properties,index]) => {
    if (!geometries[index]) throw new Error('Invalid geometry reference in polity package');
    return {type:'Feature',id:properties.id,properties,geometry:geometries[index]};
  })};
}
export async function readPolityResponse(response) {
  if (!response.ok) throw new Error(`Polity download failed (${response.status})`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  let json;
  // A host may already have decompressed the response using Content-Encoding.
  if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
    if (!globalThis.DecompressionStream) throw new Error('This browser needs gzip decompression support for atlas data');
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    json = await new Response(stream).json();
  } else json = JSON.parse(new TextDecoder().decode(bytes));
  return unpackCollection(json);
}
