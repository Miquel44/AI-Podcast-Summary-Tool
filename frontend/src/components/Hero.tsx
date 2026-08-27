import type { Story } from '../types'

export function Hero({ story, onSelect }: { story: Story; onSelect: (story: Story) => void }) {
  return (
    <header className="relative overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(115deg, ${story.cover_from}dd 0%, ${story.cover_to}66 45%, transparent 78%), radial-gradient(90% 120% at 88% 0%, ${story.cover_to}44 0%, transparent 60%)`,
        }}
      />
      <span
        aria-hidden
        className="absolute top-10 right-10 hidden text-[11rem] opacity-25 select-none md:block"
      >
        {story.icon}
      </span>
      <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/35 to-transparent" />

      <div className="relative px-8 pt-24 pb-14 md:px-14 md:pt-32">
        <p className="font-display text-xs font-600 tracking-[0.3em] text-white/60 uppercase">
          Historia destacada
        </p>
        <h1 className="mt-3 max-w-2xl font-display text-4xl leading-[1.05] font-800 text-white md:text-6xl">
          {story.title}
        </h1>
        <p className="mt-4 max-w-lg text-base text-white/75">{story.tagline}</p>
        <div className="mt-8 flex items-center gap-3">
          <button
            onClick={() => onSelect(story)}
            className="cursor-pointer rounded-lg bg-ember px-6 py-3 font-display text-sm font-700 text-white shadow-lg shadow-ember/30 transition hover:brightness-110"
          >
            {story.status === 'ready' ? '▶ Escuchar episodio' : '▶ Generar episodio'}
          </button>
        </div>
      </div>
    </header>
  )
}
