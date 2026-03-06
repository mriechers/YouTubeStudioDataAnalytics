// src/types.ts
import { z } from 'zod';

// =============================================================================
// Core Parameter Fragments
// =============================================================================

export const VideoIdParameter = z.object({
  videoId: z.string().describe('The YouTube video ID'),
});

export const PlaylistIdParameter = z.object({
  playlistId: z.string().describe('The YouTube playlist ID'),
});

export const ChannelIdParameter = z.object({
  channelId: z.string().optional().describe('YouTube channel ID. Defaults to the authenticated user\'s channel if omitted.'),
});

export const PlaylistItemIdParameter = z.object({
  playlistItemId: z.string().describe('The playlist item ID (not the video ID). Returned by listPlaylistItems.'),
});

// =============================================================================
// Pagination
// =============================================================================

export const PaginationParameters = z.object({
  maxResults: z.number().min(1).max(50).optional().default(25)
    .describe('Maximum number of results to return (1-50, default 25)'),
  pageToken: z.string().optional()
    .describe('Token for the next page of results'),
});

// =============================================================================
// Playlist Operations
// =============================================================================

export const CreatePlaylistParameters = z.object({
  title: z.string().describe('Playlist title'),
  description: z.string().optional().describe('Playlist description'),
  privacyStatus: z.enum(['public', 'unlisted', 'private']).optional().default('private')
    .describe('Privacy status (default: private)'),
});

export const AddToPlaylistParameters = z.object({
  playlistId: z.string().describe('The playlist to add the video to'),
  videoId: z.string().describe('The video ID to add'),
  position: z.number().min(0).optional()
    .describe('Position in the playlist (0-based). Omit to add at the end.'),
});

export const ReorderPlaylistItemParameters = z.object({
  playlistItemId: z.string().describe('The playlist item ID to reorder'),
  playlistId: z.string().describe('The playlist containing the item'),
  videoId: z.string().describe('The video ID of the playlist item'),
  newPosition: z.number().min(0).describe('New position in the playlist (0-based)'),
});

// =============================================================================
// Video Metadata
// =============================================================================

export const VideoMetadataParameters = z.object({
  videoId: z.string().describe('The video ID to update'),
  title: z.string().optional().describe('New video title'),
  description: z.string().optional().describe('New video description'),
  tags: z.array(z.string()).optional().describe('New tags for the video'),
  categoryId: z.string().optional().describe('Category ID (use getVideoCategories to find valid IDs)'),
  privacyStatus: z.enum(['public', 'unlisted', 'private']).optional()
    .describe('Privacy status'),
});

export const SetThumbnailParameters = z.object({
  videoId: z.string().describe('The video ID to set the thumbnail for'),
  imageBase64: z.string().describe('Base64-encoded image data (JPEG, PNG, or BMP, max 2MB)'),
  mimeType: z.enum(['image/jpeg', 'image/png', 'image/bmp']).optional().default('image/jpeg')
    .describe('MIME type of the image'),
});

// =============================================================================
// Search / Discovery
// =============================================================================

export const SearchParameters = z.object({
  query: z.string().describe('Search query'),
  type: z.enum(['video', 'channel', 'playlist']).optional().default('video')
    .describe('Type of resource to search for'),
  channelId: z.string().optional()
    .describe('Restrict search to a specific channel'),
  maxResults: z.number().min(1).max(50).optional().default(10)
    .describe('Maximum results (1-50, default 10)'),
  pageToken: z.string().optional()
    .describe('Token for the next page of results'),
  order: z.enum(['date', 'rating', 'relevance', 'title', 'viewCount']).optional().default('relevance')
    .describe('Sort order (default: relevance)'),
});

export const ListChannelVideosParameters = z.object({
  channelId: z.string().optional()
    .describe('Channel ID. Defaults to authenticated user\'s channel.'),
  maxResults: z.number().min(1).max(50).optional().default(25)
    .describe('Maximum results (1-50, default 25)'),
  pageToken: z.string().optional()
    .describe('Token for the next page of results'),
  order: z.enum(['date', 'rating', 'relevance', 'title', 'viewCount']).optional().default('date')
    .describe('Sort order (default: date)'),
});

// =============================================================================
// Video Upload
// =============================================================================

export const UploadVideoParameters = z.object({
  filePath: z.string().describe('Absolute path to the video file on disk (e.g. MP4, MOV, AVI, MKV, WebM)'),
  title: z.string().describe('Video title (max 100 characters)'),
  description: z.string().optional().default('').describe('Video description'),
  tags: z.array(z.string()).optional().describe('Tags for the video'),
  categoryId: z.string().optional().default('22').describe('Category ID (default: 22 = People & Blogs). Use getVideoCategories to find valid IDs.'),
  privacyStatus: z.enum(['public', 'unlisted', 'private']).optional().default('private')
    .describe('Privacy status (default: private — uploads as a draft)'),
  playlistId: z.string().optional().describe('Optional playlist ID to add the video to after upload'),
  notifySubscribers: z.boolean().optional().default(false)
    .describe('Whether to send a notification to subscribers (default: false)'),
});

// =============================================================================
// Categories
// =============================================================================

export const VideoCategoriesParameters = z.object({
  regionCode: z.string().optional().default('US')
    .describe('ISO 3166-1 alpha-2 country code (default: US)'),
});
