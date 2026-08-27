import type { Show } from '../types'
import { ShowCard } from './ShowCard'

export function ShowRow({
  label,
  shows,
  onSelect,
}: {
  label: string
  shows: Show[]
  onSelect: (show: Show) => void
}) {
  if (shows.length === 0) return null
  return (
    <section className="mt-10">
      <h2 className="mb-4 px-8 font-display text-sm font-600 tracking-[0.2em] text-cream-dim uppercase md:px-14">
        {label}
      </h2>
      <div className="row-scroll flex gap-4 overflow-x-auto px-8 pb-2 md:px-14">
        {shows.map((show) => (
          <ShowCard key={show.id} show={show} onClick={() => onSelect(show)} />
        ))}
      </div>
    </section>
  )
}
