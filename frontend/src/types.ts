export interface Host {
  voice_id: string
  voice_name: string
  persona: string
}

export interface Show {
  id: number
  slug: string
  title: string
  tagline: string
  interest_prompt: string
  category: 'tech' | 'finance' | 'politics' | 'history'
  kind: 'news' | 'evergreen'
  cover_from: string
  cover_to: string
  cover_icon: string
  cover_image: string | null
  hosts: Host[]
  enabled: boolean
}

export interface Episode {
  id: number
  show_id: number
  title: string
  status: 'queued' | 'fetching' | 'scripting' | 'tts' | 'ready' | 'failed'
  audio_path: string | null
  duration_s: number | null
  created_at: string
}

export interface AppSettings {
  default_voice_id: string | null
  default_voice_name: string | null
}

export const CATEGORY_LABELS: Record<Show['category'], string> = {
  tech: 'Tecnología e IA',
  finance: 'Finanzas',
  politics: 'Política',
  history: 'Historia',
}

export const CATEGORY_ORDER: Show['category'][] = ['tech', 'finance', 'politics', 'history']
