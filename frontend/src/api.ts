import type { AppSettings, Episode, Show } from './types'

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const api = {
  shows: () => fetch('/api/shows').then((r) => json<Show[]>(r)),
  episodes: (showId: number) =>
    fetch(`/api/shows/${showId}/episodes`).then((r) => json<Episode[]>(r)),
  updateShow: (showId: number, patch: Partial<Show>) =>
    fetch(`/api/shows/${showId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    }).then((r) => json<Show>(r)),
  settings: () => fetch('/api/settings').then((r) => json<AppSettings>(r)),
}
