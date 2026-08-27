import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import { CategoryRow } from './components/CategoryRow'
import { Hero } from './components/Hero'
import { StoryModal } from './components/StoryModal'
import type { Category, Story } from './types'

export default function App() {
  const [categories, setCategories] = useState<Category[]>([])
  const [storiesByCat, setStoriesByCat] = useState<Record<number, Story[]>>({})
  const [selected, setSelected] = useState<Story | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadStories = useCallback(async (cats: Category[]) => {
    const entries = await Promise.all(
      cats.map(async (c) => [c.id, await api.stories(c.id).catch(() => [])] as const),
    )
    setStoriesByCat(Object.fromEntries(entries))
  }, [])

  const refreshAll = useCallback(() => {
    if (categories.length) loadStories(categories)
  }, [categories, loadStories])

  useEffect(() => {
    api
      .categories()
      .then((cats) => {
        setCategories(cats)
        return loadStories(cats)
      })
      .catch((e) => setError(String(e)))
  }, [loadStories])

  // The backend prepares the daily edition on its own; poll quietly so rows
  // fill in and card statuses update without any user action.
  useEffect(() => {
    if (!categories.length) return
    const t = setInterval(() => loadStories(categories), 6000)
    return () => clearInterval(t)
  }, [categories, loadStories])

  const handleDiscover = async (category: Category) => {
    try {
      await api.discover(category.id)
      const stories = await api.stories(category.id)
      setStoriesByCat((prev) => ({ ...prev, [category.id]: stories }))
    } catch (e) {
      setError(`Descubrimiento falló en ${category.title}: ${String(e)}`)
    }
  }

  const allStories = Object.values(storiesByCat).flat()
  const featured =
    allStories.find((s) => s.status === 'ready') ??
    allStories.find((s) => s.status === 'generating') ??
    allStories[0]

  return (
    <div className="min-h-screen bg-ink font-body text-cream">
      <nav className="absolute top-0 right-0 left-0 z-20 flex items-center justify-between px-8 py-6 md:px-14">
        <span className="font-display text-xl font-800 tracking-[0.35em] text-white">ONDA</span>
        <div className="flex items-center gap-6 text-sm text-white/60">
          <button className="cursor-pointer transition hover:text-white">Ajustes</button>
          <button className="cursor-pointer transition hover:text-white">Dashboard</button>
        </div>
      </nav>

      {error && (
        <div className="fixed right-4 bottom-4 z-50 max-w-sm rounded-lg bg-red-950/90 p-3 text-xs text-red-200 shadow-xl">
          {error}
          <button onClick={() => setError(null)} className="ml-2 cursor-pointer font-bold">
            ✕
          </button>
        </div>
      )}

      {featured ? (
        <Hero story={featured} onSelect={setSelected} />
      ) : (
        <div className="px-8 pt-28 pb-4 md:px-14">
          <h1 className="max-w-2xl font-display text-4xl leading-tight font-800 text-white">
            Tu emisora personal
          </h1>
          <p className="mt-3 max-w-lg text-white/60">
            Pulsa «Descubrir» en cualquier categoría para buscar las historias de hoy.
          </p>
        </div>
      )}

      <main className="pb-20">
        {categories.map((cat) => (
          <CategoryRow
            key={cat.id}
            category={cat}
            stories={storiesByCat[cat.id] ?? []}
            onDiscover={handleDiscover}
            onSelect={setSelected}
          />
        ))}
      </main>

      {selected && (
        <StoryModal
          storyId={selected.id}
          category={categories.find((c) => c.id === selected.category_id)}
          onClose={() => setSelected(null)}
          onChanged={refreshAll}
        />
      )}
    </div>
  )
}
