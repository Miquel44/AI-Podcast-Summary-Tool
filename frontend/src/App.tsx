import { useEffect, useState } from 'react'
import { api } from './api'
import { Hero } from './components/Hero'
import { ShowRow } from './components/ShowRow'
import { CATEGORY_LABELS, CATEGORY_ORDER, type Show } from './types'

export default function App() {
  const [shows, setShows] = useState<Show[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.shows().then(setShows).catch((e) => setError(String(e)))
  }, [])

  const featured = shows.find((s) => s.category === 'tech') ?? shows[0]

  const handleSelect = (show: Show) => {
    // Show detail / voice picker page lands in the next iteration.
    console.log('selected show', show.slug)
  }

  return (
    <div className="min-h-screen bg-ink font-body text-cream">
      <nav className="absolute top-0 right-0 left-0 z-20 flex items-center justify-between px-8 py-6 md:px-14">
        <span className="font-display text-xl font-800 tracking-[0.35em] text-white">
          ONDA
        </span>
        <div className="flex items-center gap-6 text-sm text-white/60">
          <button className="cursor-pointer transition hover:text-white">Episodios</button>
          <button className="cursor-pointer transition hover:text-white">Ajustes</button>
          <button className="cursor-pointer transition hover:text-white">Dashboard</button>
        </div>
      </nav>

      {error && (
        <div className="px-8 pt-28 text-sm text-ember md:px-14">
          No se pudo cargar el catálogo: {error}. ¿Está el backend en marcha?
        </div>
      )}

      {featured && <Hero show={featured} onSelect={handleSelect} />}

      <main className="pb-20">
        {CATEGORY_ORDER.map((cat) => (
          <ShowRow
            key={cat}
            label={CATEGORY_LABELS[cat]}
            shows={shows.filter((s) => s.category === cat)}
            onSelect={handleSelect}
          />
        ))}
      </main>
    </div>
  )
}
