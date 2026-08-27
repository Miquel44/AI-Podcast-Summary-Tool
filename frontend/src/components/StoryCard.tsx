import type { Story } from '../types'

const STATUS_CHIP: Record<Story['status'], { label: string; cls: string } | null> = {
  suggested: null,
  generating: { label: '● Generando…', cls: 'bg-amber-400/90 text-black animate-pulse' },
  ready: { label: '▶ Listo', cls: 'bg-emerald-400/90 text-black' },
  failed: { label: '⚠ Error', cls: 'bg-red-500/90 text-white' },
}

export function StoryCard({ story, onClick }: { story: Story; onClick: () => void }) {
  const angle = 130 + ((story.id * 37) % 60) // varied light direction per card
  const chip = STATUS_CHIP[story.status]

  return (
    <button
      onClick={onClick}
      className="group relative w-44 shrink-0 cursor-pointer overflow-hidden rounded-xl text-left shadow-lg shadow-black/40 transition-all duration-300 ease-out hover:z-10 hover:scale-[1.07] hover:shadow-2xl hover:shadow-black/60 focus-visible:scale-105 focus-visible:outline-2 focus-visible:outline-ember md:w-52"
      style={{ aspectRatio: '2 / 3' }}
    >
      <div
        className="absolute inset-0 transition-transform duration-500 group-hover:scale-105"
        style={{
          background: `linear-gradient(${angle}deg, ${story.cover_from} 0%, ${story.cover_to} 100%)`,
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(130% 90% at 25% 8%, rgba(255,255,255,0.28) 0%, transparent 55%), radial-gradient(80% 60% at 85% 95%, rgba(0,0,0,0.35) 0%, transparent 60%)',
        }}
      />
      <span
        aria-hidden
        className="absolute -right-5 top-6 select-none text-[6.5rem] opacity-55 drop-shadow-lg transition-transform duration-300 group-hover:rotate-6 group-hover:scale-110"
      >
        {story.icon}
      </span>
      <div className="absolute inset-x-0 bottom-0 h-3/4 bg-gradient-to-t from-black/85 via-black/30 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 p-4">
        <h3 className="font-display text-[17px] leading-tight font-700 text-white drop-shadow-sm">
          {story.title}
        </h3>
        <p className="mt-1.5 line-clamp-3 text-xs leading-snug text-white/75 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          {story.tagline}
        </p>
      </div>
      {chip && (
        <span
          className={`absolute top-3 left-3 rounded-full px-2.5 py-1 text-[11px] font-semibold tracking-wide backdrop-blur-sm ${chip.cls}`}
        >
          {chip.label}
        </span>
      )}
    </button>
  )
}
