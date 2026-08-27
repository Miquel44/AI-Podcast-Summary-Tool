import type { AppSettings, Category, Story, StoryDetail } from './types'

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(body || `${res.status} ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  categories: () => fetch('/api/categories').then((r) => json<Category[]>(r)),
  stories: (categoryId: number) =>
    fetch(`/api/categories/${categoryId}/stories`).then((r) => json<Story[]>(r)),
  discover: (categoryId: number) =>
    fetch(`/api/categories/${categoryId}/discover`, { method: 'POST' }).then((r) =>
      json<Story[]>(r),
    ),
  story: (storyId: number) => fetch(`/api/stories/${storyId}`).then((r) => json<StoryDetail>(r)),
  generate: (storyId: number) =>
    fetch(`/api/stories/${storyId}/generate`, { method: 'POST' }).then((r) =>
      json<StoryDetail>(r),
    ),
  settings: () => fetch('/api/settings').then((r) => json<AppSettings>(r)),
}
