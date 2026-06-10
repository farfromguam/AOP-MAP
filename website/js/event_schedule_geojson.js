/* AOP event-schedule resolver — the ONE canonical transform.
 *
 * Going gold slice 6, G_E (2026-06-10). Collapses the two divergent resolvers
 * (audit `event-overlay-two-divergent-resolvers`, C1/C6) into a single pure
 * function read by BOTH surfaces:
 *   - the embedded viewer (index.html → main.js's eventScheduleToGeojson wrapper)
 *   - the standalone right panel (right_panel.html → panel.js's event-schedule source)
 *
 * It transforms the served `{schema,event,locations{},sessions[]}` document into
 * the canonical event GeoJSON: anchor Points + session route/point features +
 * a top-level `metadata` block. The document shape itself is NOT collapsed (the
 * calendar/hot-button/state-machine still read sessions[]/event.* directly); this
 * is purely the document→GeoJSON transform both maps draw.
 *
 * Coordinate priority (the `event-anchor-position-from-localstorage-tag-binding`
 * fix): an explicit `location.coordinates` in the served document WINS — it is the
 * baked truth (resolved at bake from each event-place row's geom). When a location
 * has no coordinates AND a caller supplies `opts.resolveTagCoords(tag)`, that hook
 * fills them as a WORKING-BUFFER override (the host's localStorage `tagToFeature`
 * binding). The panel passes no hook, so the standalone map relies purely on baked
 * coordinates. localStorage is thus an override, never the source of an anchor's
 * position.
 *
 * No module imports — plain `window.AOPEventSchedule` namespace so both vanilla-JS
 * IIFE pages (main.js, panel.js) reach the same code without a bundler (C6: this is
 * the one shared transform, not a second registry / class hierarchy / editor surface).
 */
(function () {
  'use strict';

  function normalizeLocationTag(tag) {
    const value = String(tag || '').trim();
    if (!value) return '';
    return value.startsWith('#') ? value : `#${value}`;
  }

  // Resolve a single location entry, following `alias_of` chains. `resolveTagCoords`
  // (optional) is the working-buffer fallback for a coordinate-less tag; baked
  // `coordinates` always win when present.
  function resolveEventLocation(config, tag, resolveTagCoords, seen) {
    seen = seen || new Set();
    const normalized = normalizeLocationTag(tag);
    if (!normalized || seen.has(normalized)) return null;
    const raw = config && config.locations ? config.locations[normalized] : null;
    if (!raw) return null;
    if (raw.alias_of) {
      seen.add(normalized);
      const base = resolveEventLocation(config, raw.alias_of, resolveTagCoords, seen);
      if (!base) return null;
      return Object.assign({}, base, raw, {
        tag: normalized,
        coordinates: raw.coordinates || base.coordinates,
        label: raw.label || base.label,
        map_label: raw.map_label || raw.label || base.map_label || base.label,
        role: raw.role || base.role
      });
    }
    const resolved = Object.assign({}, raw, { tag: normalized });
    // Baked coordinates win. Only when absent do we consult the working buffer.
    if (!resolved.coordinates && typeof resolveTagCoords === 'function') {
      const coords = resolveTagCoords(normalized);
      if (Array.isArray(coords) && coords.length >= 2) {
        resolved.coordinates = [coords[0], coords[1]];
        resolved.bound_from_buffer = true;
      }
    }
    return resolved;
  }

  function buildEventLocationIndex(config, resolveTagCoords) {
    const byTag = new Map();
    const locs = (config && config.locations) || {};
    for (const tag of Object.keys(locs)) {
      const location = resolveEventLocation(config, tag, resolveTagCoords);
      if (location) byTag.set(normalizeLocationTag(tag), location);
    }
    return byTag;
  }

  function eventDayShort(label) {
    const clean = String(label || '').trim();
    return clean.length <= 3 ? clean : clean.slice(0, 3);
  }

  function formatEventStartLocal(start) {
    const text = String(start || '').trim();
    if (!text) return '';
    const match = /^(\d{1,2}):(\d{2})$/.exec(text);
    if (!match) return text;
    const hour = Number(match[1]);
    const minute = Number(match[2]);
    if (!Number.isFinite(hour) || hour < 0 || hour > 23 || !Number.isFinite(minute) || minute < 0 || minute > 59) return text;
    const period = hour >= 12 ? 'PM' : 'AM';
    const hour12 = ((hour + 11) % 12) + 1;
    const minuteStr = String(minute).padStart(2, '0');
    return `${hour12}:${minuteStr} ${period}`;
  }

  function composeEventWindowLabel(start, timeLabel) {
    const clock = formatEventStartLocal(start);
    const label = String(timeLabel || '').trim();
    if (clock && label) return `${clock} · ${label}`;
    return clock || label;
  }

  function eventRouteCoordinates(session, byTag) {
    const tags = Array.isArray(session.route_tags) ? session.route_tags : [];
    const coords = [];
    for (const tag of tags) {
      const location = byTag.get(normalizeLocationTag(tag));
      if (location && location.coordinates) coords.push(location.coordinates);
    }
    return coords;
  }

  // The ONE canonical transform. Returns the GeoJSON FeatureCollection plus the
  // location/session indexes the host re-uses for its module-scoped maps (so the
  // host does not recompute them from a divergent path).
  //   config: the served {schema,event,locations,sessions} document
  //   opts.resolveTagCoords(normalizedTag) -> [lng,lat] | null  (optional buffer)
  function eventScheduleToGeojson(config, opts) {
    opts = opts || {};
    const resolveTagCoords = opts.resolveTagCoords;
    const byTag = buildEventLocationIndex(config, resolveTagCoords);
    const sessionById = new Map();
    const features = [];
    const event = (config && config.event) || {};

    for (const [tag, location] of byTag.entries()) {
      if (location.hidden || !location.coordinates) continue;
      features.push({
        type: 'Feature',
        properties: {
          feature_kind: 'event_anchor',
          event_id: event.id || '',
          location_tag: tag,
          name: location.label || tag,
          map_label: location.map_label || location.label || tag,
          role: location.role || 'event_location',
          source: location.source || '',
          confidence: location.confidence || (config && config.status) || 'proposed',
          caveat: location.caveat || event.caveat || ''
        },
        geometry: { type: 'Point', coordinates: location.coordinates }
      });
    }

    for (const session of (config && config.sessions) || []) {
      const tag = normalizeLocationTag(session.location_tag);
      const location = byTag.get(tag);
      const routeCoords = eventRouteCoordinates(session, byTag);
      const geometry = routeCoords.length >= 2
        ? { type: 'LineString', coordinates: routeCoords }
        : location && location.coordinates
          ? { type: 'Point', coordinates: location.coordinates }
          : null;
      const props = {
        feature_kind: 'event_session',
        event_id: event.id || '',
        session_id: session.id || '',
        sort_order: Number(session.sort_order || 0),
        day: session.date_label || '',
        day_short: session.day_short || eventDayShort(session.date_label),
        start_local: session.start_local || '',
        time_label: session.time_label || '',
        window: composeEventWindowLabel(session.start_local, session.time_label),
        name: session.title || '',
        title: session.title || '',
        location_tag: tag,
        location_label: (location && location.label) || `Missing ${tag}`,
        route_tags: Array.isArray(session.route_tags) ? session.route_tags.map(normalizeLocationTag) : [],
        route_labels: routeCoords.length >= 2
          ? session.route_tags.map((routeTag) => {
              const l = byTag.get(normalizeLocationTag(routeTag));
              return (l && l.label) || normalizeLocationTag(routeTag);
            })
          : [],
        poi_role: session.poi_role || (location && location.role) || 'event_session',
        status: session.status || (config && config.status) || 'proposed',
        inspired_by: session.inspired_by || [],
        caveat: session.caveat || (location && location.caveat) || event.caveat || ''
      };
      const feature = { type: 'Feature', properties: props, geometry };
      features.push(feature);
      if (props.session_id) sessionById.set(props.session_id, feature);
    }

    const geojson = {
      type: 'FeatureCollection',
      metadata: {
        schema: (config && config.schema) || 'aop-event-schedule-v1',
        updated_at: (config && config.updated_at) || '',
        status: (config && config.status) || 'proposed',
        event
      },
      features
    };
    return { geojson, locationByTag: byTag, sessionById };
  }

  window.AOPEventSchedule = {
    eventScheduleToGeojson,
    resolveEventLocation,
    buildEventLocationIndex,
    normalizeLocationTag,
    eventRouteCoordinates,
    composeEventWindowLabel,
    formatEventStartLocal,
    eventDayShort
  };
})();
