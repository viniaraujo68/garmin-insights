import type { Privacy } from "$lib/data/types";

const EARTH_RADIUS_M = 6_371_000;
const radians = (degrees: number): number => (degrees * Math.PI) / 180;

export const distanceM = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const h =
    Math.sin(radians(lat2 - lat1) / 2) ** 2 +
    Math.cos(radians(lat1)) * Math.cos(radians(lat2)) * Math.sin(radians(lon2 - lon1) / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(h));
};

export const isPrivate = (
  privacy: Privacy | null,
  lat: number | null | undefined,
  lon: number | null | undefined,
): boolean =>
  privacy !== null &&
  lat !== null &&
  lat !== undefined &&
  lon !== null &&
  lon !== undefined &&
  distanceM(privacy.lat, privacy.lon, lat, lon) <= privacy.radius_m;
