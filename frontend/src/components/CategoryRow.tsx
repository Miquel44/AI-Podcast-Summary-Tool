import { useRef, useState } from 'react'
import type { Strings } from '../i18n'
import type { Category, Story } from '../types'
import { StoryCard } from './StoryCard'

export function CategoryRow({
  category,
  stories,
  onDiscover,
  onSelect,
  t,
}: {
  category: Category
  stories: Story[]
  onDiscover: (category: Category) => Promise<void>
  onSelect: (story: Story) => void
  t: Strings
}) {
  const scroller = useRef<HTMLDivElement>(null)
  const [discovering, setDiscovering] = useState(false)

  const scrollBy = (dir: 1 | -1) => {
    const el = scroller.current
    if (el) el.scrollBy({ left: dir * el.clientWidth * 0.8, behavior: 'smooth' })
  }

  const discover = async () => {
    setDiscovering(true)
    try {
      await onDiscover(category)
    } finally {
      setDiscovering(false)
    }
  }

  return (
    <section className="group/row relative mt-10">
      <div className="mb-3 flex items-baseline gap-4 px-8 md:px-14">
        <h2 className="font-display text-sm font-600 tracking-[0.2em] text-cream-dim uppercase">
          {category.title}
        </h2>
        <button
          onClick={discover}
          disabled={discovering}
          className="cursor-pointer text-xs font-medium text-white/40 transition hover:text-ember disabled:cursor-wait disabled:text-amber-400"
        >
          {discovering ? t.refreshing : t.refresh}
        </button>
      </div>

      <div className="relative">
        {stories.length > 0 && (
          <>
            <RowArrow dir={-1} onClick={() => scrollBy(-1)} />
            <RowArrow dir={1} onClick={() => scrollBy(1)} />
          </>
        )}
        <div ref={scroller} className="row-scroll flex gap-4 overflow-x-auto px-8 pb-3 md:px-14">
          {stories.map((story) => (
            <StoryCard key={story.id} story={story} onClick={() => onSelect(story)} t={t} />
          ))}
          {stories.length === 0 &&
            Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="shimmer relative w-44 shrink-0 rounded-xl md:w-52"
                style={{ aspectRatio: '2 / 3' }}
              >
                {i === 0 && (
                  <span className="absolute inset-x-0 bottom-4 px-4 text-center font-display text-xs font-600 text-white/35">
                    {t.preparing}
                  </span>
                )}
              </div>
            ))}
        </div>
      </div>
    </section>
  )
}

function RowArrow({ dir, onClick }: { dir: 1 | -1; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      aria-label={dir === 1 ? 'Desplazar a la derecha' : 'Desplazar a la izquierda'}
      className={`absolute top-0 bottom-3 z-20 hidden w-12 cursor-pointer items-center justify-center bg-gradient-to-r text-2xl text-white/0 transition group-hover/row:text-white/90 md:flex ${
        dir === 1
          ? 'right-0 from-transparent to-ink/90'
          : 'left-0 from-ink/90 to-transparent'
      }`}
    >
      {dir === 1 ? '›' : '‹'}
    </button>
  )
}
