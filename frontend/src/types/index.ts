export interface User {
  id: string
  email: string
  name: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export type Platform = 'instagram' | 'youtube' | 'tiktok' | 'x' | 'threads' | 'snapchat'

export const PLATFORM_META: Record<Platform, { label: string; color: string; icon: string }> = {
  instagram: { label: 'Instagram', color: 'bg-pink-500',      icon: '📸' },
  youtube:   { label: 'YouTube',   color: 'bg-red-500',       icon: '▶️' },
  tiktok:    { label: 'TikTok',    color: 'bg-black',         icon: '🎵' },
  x:         { label: 'X',         color: 'bg-neutral-800',   icon: '𝕏' },
  threads:   { label: 'Threads',   color: 'bg-neutral-700',   icon: '🧵' },
  snapchat:  { label: 'Snapchat',  color: 'bg-yellow-400',    icon: '👻' },
}

export interface SocialAccount {
  id: string
  user_id: string
  platform: Platform
  platform_user_id: string
  username: string
  display_name: string | null
  profile_image_url: string | null
  biography: string | null
  followers_count: number
  is_active: boolean
  last_synced_at: string | null
  created_at: string
  updated_at: string
}

export interface SocialAccountCreate {
  platform: Platform
  platform_user_id: string
  username: string
  display_name?: string
  profile_image_url?: string
  access_token: string
  refresh_token?: string
  token_expires_at?: string
  facebook_page_id?: string
  instagram_business_id?: string
}

export type UploadStatus = 'pending' | 'ready' | 'failed'
export type MediaType = 'video' | 'image'

export interface Upload {
  id: string
  user_id: string
  original_filename: string
  file_path: string
  file_size_bytes: number | null
  mime_type: string | null
  duration_seconds: number | null
  thumbnail_path: string | null
  media_type: MediaType
  title: string | null
  description: string | null
  hashtags: string[] | null
  status: UploadStatus
  error_message: string | null
  created_at: string
  updated_at: string
}

export type PostStatus = 'queued' | 'publishing' | 'published' | 'failed'

export interface Post {
  id: string
  upload_id: string
  social_account_id: string
  caption: string | null
  status: PostStatus
  platform_post_id: string | null
  error_message: string | null
  published_at: string | null
  created_at: string
  updated_at: string
}

export interface PublishRequest {
  upload_id: string
  account_ids: string[]
  title?: string
  description?: string
  hashtags?: string[]
  caption?: string
}
