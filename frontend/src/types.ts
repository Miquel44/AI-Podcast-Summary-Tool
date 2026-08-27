export interface Host {
  voice_id: string
  voice_name: string
  persona: string
}

export interface Category {
  id: number
  slug: string
  title: string
  interest_prompt: string
  kind: 'news' | 'evergreen'
  hosts: Host[]
  enabled: boolean
  position: number
}

export type StoryStatus = 'suggested' | 'generating' | 'ready' | 'failed'

export interface SourceArticle {
  title: string
  url: string
  source: string
}

export interface Story {
  id: number
  category_id: number
  title: string
  tagline: string
  summary: string
  icon: string
  cover_from: string
  cover_to: string
  cover_image: string | null
  cover_credit: string | null
  source_articles: SourceArticle[]
  status: StoryStatus
  created_at: string
}

export interface Episode {
  id: number
  story_id: number
  title: string
  script: { host: number; text: string }[]
  audio_path: string | null
  duration_s: number | null
  error: string | null
  created_at: string
}

export interface StoryDetail extends Story {
  episodes: Episode[]
}

export interface AppSettings {
  default_voice_id: string | null
  default_voice_name: string | null
  language: string
}
