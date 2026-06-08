// ─── Platform ────────────────────────────────────────────────────────────────

export type Platform = "instagram" | "facebook" | "tiktok";

export const PLATFORM_LABELS: Record<Platform, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
};

// ─── Social Account ───────────────────────────────────────────────────────────

export interface SocialAccountSummary {
  id: string;
  platform: Platform;
  username: string;
  display_name: string | null;
  profile_image_url: string | null;
  is_active: boolean;
}

export interface SocialAccount extends SocialAccountSummary {
  device_id: string;
  platform_user_id: string;
  biography: string | null;
  followers_count: number;
  following_count: number;
  media_count: number;
  facebook_page_id: string | null;
  instagram_business_id: string | null;
  scopes: string[] | null;
  token_expires_at: string | null;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SyncResponse {
  account: SocialAccount;
  synced: boolean;
}

// ─── Device ──────────────────────────────────────────────────────────────────

export interface Device {
  id: string;
  name: string;
  description: string | null;
  meta: Record<string, unknown>;
  social_accounts: SocialAccountSummary[];
  created_at: string;
  updated_at: string;
}

export interface DeviceCreate {
  name: string;
  description?: string;
  meta?: Record<string, unknown>;
}

export interface DeviceUpdate {
  name?: string;
  description?: string;
  meta?: Record<string, unknown>;
}

// ─── Upload ───────────────────────────────────────────────────────────────────

export type UploadStatus = "pending" | "ready" | "failed";
export type MediaType = "video" | "image";

export interface Upload {
  id: string;
  original_filename: string;
  file_path: string;
  file_size_bytes: number | null;
  mime_type: string | null;
  duration_seconds: number | null;
  thumbnail_path: string | null;
  media_type: MediaType;
  caption: string | null;
  status: UploadStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// ─── Post ────────────────────────────────────────────────────────────────────

export type PostStatus = "queued" | "publishing" | "published" | "failed";

export interface Post {
  id: string;
  upload_id: string;
  social_account_id: string;
  caption: string | null;
  status: PostStatus;
  platform_post_id: string | null;
  error_message: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PublishRequest {
  upload_id: string;
  account_ids: string[];
  caption?: string;
}

export interface PublishResponse {
  posts: Post[];
  succeeded: number;
  failed: number;
}

// ─── Activity Log ─────────────────────────────────────────────────────────────

export interface ActivityLog {
  id: string;
  event_type: string;
  resource_type: string | null;
  resource_id: string | null;
  description: string | null;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

// ─── Instagram Media ──────────────────────────────────────────────────────────

export type InstagramMediaType = "IMAGE" | "VIDEO" | "CAROUSEL_ALBUM" | "REELS";

export interface InstagramMediaItem {
  id: string;
  media_type: InstagramMediaType;
  media_url: string | null;
  thumbnail_url: string | null;
  permalink: string | null;
  timestamp: string | null;
  like_count: number | null;
  comments_count: number | null;
  caption: string | null;
}

export interface MediaFeedResponse {
  account_id: string;
  platform: Platform;
  items: InstagramMediaItem[];
}

export interface TokenRefreshResponse {
  account_id: string;
  platform: string;
  refreshed: boolean;
  message: string;
}

// ─── Content Library ──────────────────────────────────────────────────────────

export type ContentFileType = "video" | "audio";
export type ContentFileStatus =
  | "pending"
  | "analyzing"
  | "analyzed"
  | "matched"
  | "queued"
  | "posted"
  | "failed";

export interface ContentFolder {
  id: string;
  path: string;
  label: string;
  is_active: boolean;
  last_scanned_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContentFolderCreate {
  path: string;
  label: string;
}

export interface ContentFile {
  id: string;
  folder_id: string;
  filename: string;
  file_path: string;
  file_type: ContentFileType;
  file_size_bytes: number | null;
  duration_seconds: number | null;
  mime_type: string | null;
  content_hash: string | null;
  thumbnail_path: string | null;
  status: ContentFileStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScanResult {
  added: number;
  updated: number;
  skipped: number;
}

export interface AiAnalysis {
  id: string;
  content_file_id: string;
  scenes: string[] | null;
  objects: string[] | null;
  activities: string[] | null;
  emotions: string[] | null;
  genre: string | null;
  category: string | null;
  summary: string | null;
  keywords: string[] | null;
  target_audience: string | null;
  viral_potential_score: number | null;
  model_used: string | null;
  analyzed_at: string | null;
  created_at: string;
  updated_at: string;
}

export type ContentPlatform =
  | "instagram"
  | "tiktok"
  | "youtube"
  | "x"
  | "threads"
  | "snapchat";

export interface GeneratedContent {
  id: string;
  content_file_id: string;
  platform: ContentPlatform;
  hook: string | null;
  caption: string | null;
  cta: string | null;
  title: string | null;
  hashtags: string[] | null;
  created_at: string;
  updated_at: string;
}

// ─── API ─────────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  platform?: string;
}
