// src/server.ts
import { FastMCP, UserError } from 'fastmcp';
import { z } from 'zod';
import { google, youtube_v3 } from 'googleapis';
import { authorize } from './auth.js';
import { Readable } from 'stream';

import {
  VideoIdParameter,
  PlaylistIdParameter,
  ChannelIdParameter,
  PlaylistItemIdParameter,
  PaginationParameters,
  CreatePlaylistParameters,
  AddToPlaylistParameters,
  ReorderPlaylistItemParameters,
  VideoMetadataParameters,
  SetThumbnailParameters,
  SearchParameters,
  ListChannelVideosParameters,
  VideoCategoriesParameters,
  UploadVideoParameters,
} from './types.js';

import * as fs from 'fs';
import * as path from 'path';

// --- YouTube API Client ---

let youtubeClient: youtube_v3.Youtube | null = null;

async function initializeYouTubeClient(): Promise<youtube_v3.Youtube> {
  if (youtubeClient) return youtubeClient;
  try {
    console.error('Attempting to authorize YouTube API client...');
    const auth = await authorize();
    youtubeClient = google.youtube({ version: 'v3', auth });
    console.error('YouTube API client authorized successfully.');
    return youtubeClient;
  } catch (error) {
    console.error('FATAL: Failed to initialize YouTube API client:', error);
    youtubeClient = null;
    throw new Error('YouTube client initialization failed. Cannot start server tools.');
  }
}

// --- Error Handling ---

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Promise Rejection:', reason);
});

// --- Helper: resolve channel ID (defaults to authenticated user) ---

async function resolveChannelId(yt: youtube_v3.Youtube, channelId?: string): Promise<string> {
  if (channelId) return channelId;
  const res = await yt.channels.list({ part: ['id'], mine: true });
  const id = res.data.items?.[0]?.id;
  if (!id) throw new UserError('Could not determine authenticated channel ID. Provide channelId explicitly.');
  return id;
}

// =============================================================================
// FastMCP Server
// =============================================================================

const server = new FastMCP({
  name: 'YouTube MCP Server',
  version: '1.0.0',
});

// =============================================================================
// PLAYLIST MANAGEMENT (8 tools)
// =============================================================================

// --- listPlaylists ---
server.addTool({
  name: 'listPlaylists',
  description: 'List all playlists owned by the authenticated channel, or by a specific channel. Returns playlist ID, title, description, item count, and privacy status.',
  parameters: ChannelIdParameter.merge(PaginationParameters),
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const params: youtube_v3.Params$Resource$Playlists$List = {
      part: ['snippet', 'contentDetails', 'status'],
      maxResults: args.maxResults,
      pageToken: args.pageToken,
    };
    if (args.channelId) {
      params.channelId = args.channelId;
    } else {
      params.mine = true;
    }
    const res = await yt.playlists.list(params);
    const playlists = (res.data.items || []).map((p) => ({
      id: p.id,
      title: p.snippet?.title,
      description: p.snippet?.description,
      itemCount: p.contentDetails?.itemCount,
      privacyStatus: p.status?.privacyStatus,
      publishedAt: p.snippet?.publishedAt,
    }));
    return JSON.stringify({
      playlists,
      nextPageToken: res.data.nextPageToken,
      totalResults: res.data.pageInfo?.totalResults,
    }, null, 2);
  },
});

// --- getPlaylist ---
server.addTool({
  name: 'getPlaylist',
  description: 'Get details for a specific playlist by ID. Returns title, description, item count, privacy status, and channel info.',
  parameters: PlaylistIdParameter,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const res = await yt.playlists.list({
      part: ['snippet', 'contentDetails', 'status'],
      id: [args.playlistId],
    });
    const playlist = res.data.items?.[0];
    if (!playlist) throw new UserError(`Playlist not found: ${args.playlistId}`);
    return JSON.stringify({
      id: playlist.id,
      title: playlist.snippet?.title,
      description: playlist.snippet?.description,
      channelId: playlist.snippet?.channelId,
      channelTitle: playlist.snippet?.channelTitle,
      itemCount: playlist.contentDetails?.itemCount,
      privacyStatus: playlist.status?.privacyStatus,
      publishedAt: playlist.snippet?.publishedAt,
    }, null, 2);
  },
});

// --- createPlaylist ---
server.addTool({
  name: 'createPlaylist',
  description: 'Create a new playlist on the authenticated channel. Returns the new playlist ID.',
  parameters: CreatePlaylistParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const res = await yt.playlists.insert({
      part: ['snippet', 'status'],
      requestBody: {
        snippet: {
          title: args.title,
          description: args.description || '',
        },
        status: {
          privacyStatus: args.privacyStatus,
        },
      },
    });
    return JSON.stringify({
      id: res.data.id,
      title: res.data.snippet?.title,
      privacyStatus: res.data.status?.privacyStatus,
      url: `https://www.youtube.com/playlist?list=${res.data.id}`,
    }, null, 2);
  },
});

// --- deletePlaylist (DISABLED) ---
server.addTool({
  name: 'deletePlaylist',
  description: '⛔ DISABLED FOR SAFETY — Playlist deletion is disabled. Delete manually via YouTube Studio.',
  parameters: PlaylistIdParameter,
  execute: async (args, { log }) => {
    log.warn(`deletePlaylist called but is disabled. Playlist ID: ${args.playlistId}`);
    throw new UserError(
      "🛡️ PLAYLIST DELETION IS DISABLED FOR SAFETY\n\n" +
      "Alternatives:\n" +
      "• Set playlist to 'private' by creating a new one and migrating items\n" +
      "• Delete manually via YouTube Studio (studio.youtube.com)\n\n" +
      "To enable, modify the deletePlaylist tool in server.ts and rebuild."
    );
  },
});

// --- listPlaylistItems ---
server.addTool({
  name: 'listPlaylistItems',
  description: 'List videos in a playlist with their positions. Returns video IDs, titles, positions, and playlist item IDs (needed for reorder/remove).',
  parameters: PlaylistIdParameter.merge(PaginationParameters),
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const res = await yt.playlistItems.list({
      part: ['snippet', 'contentDetails', 'status'],
      playlistId: args.playlistId,
      maxResults: args.maxResults,
      pageToken: args.pageToken,
    });
    const items = (res.data.items || []).map((item) => ({
      playlistItemId: item.id,
      videoId: item.contentDetails?.videoId,
      title: item.snippet?.title,
      description: item.snippet?.description,
      position: item.snippet?.position,
      publishedAt: item.contentDetails?.videoPublishedAt,
      privacyStatus: item.status?.privacyStatus,
    }));
    return JSON.stringify({
      items,
      nextPageToken: res.data.nextPageToken,
      totalResults: res.data.pageInfo?.totalResults,
    }, null, 2);
  },
});

// --- addToPlaylist ---
server.addTool({
  name: 'addToPlaylist',
  description: 'Add a video to a playlist. Optionally specify position (0-based). Returns the new playlist item ID.',
  parameters: AddToPlaylistParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const requestBody: youtube_v3.Schema$PlaylistItem = {
      snippet: {
        playlistId: args.playlistId,
        resourceId: {
          kind: 'youtube#video',
          videoId: args.videoId,
        },
      },
    };
    if (args.position !== undefined) {
      requestBody.snippet!.position = args.position;
    }
    const res = await yt.playlistItems.insert({
      part: ['snippet'],
      requestBody,
    });
    return JSON.stringify({
      playlistItemId: res.data.id,
      videoId: args.videoId,
      playlistId: args.playlistId,
      position: res.data.snippet?.position,
    }, null, 2);
  },
});

// --- removeFromPlaylist ---
server.addTool({
  name: 'removeFromPlaylist',
  description: 'Remove a video from a playlist by its playlist item ID (not the video ID). Use listPlaylistItems to find the playlistItemId.',
  parameters: PlaylistItemIdParameter,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    await yt.playlistItems.delete({ id: args.playlistItemId });
    return JSON.stringify({
      removed: true,
      playlistItemId: args.playlistItemId,
    }, null, 2);
  },
});

// --- reorderPlaylistItem ---
server.addTool({
  name: 'reorderPlaylistItem',
  description: 'Move a video to a new position within a playlist. Requires the playlistItemId (from listPlaylistItems), playlistId, videoId, and the new 0-based position.',
  parameters: ReorderPlaylistItemParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const res = await yt.playlistItems.update({
      part: ['snippet'],
      requestBody: {
        id: args.playlistItemId,
        snippet: {
          playlistId: args.playlistId,
          resourceId: {
            kind: 'youtube#video',
            videoId: args.videoId,
          },
          position: args.newPosition,
        },
      },
    });
    return JSON.stringify({
      playlistItemId: res.data.id,
      newPosition: res.data.snippet?.position,
    }, null, 2);
  },
});

// =============================================================================
// VIDEO DISCOVERY (3 tools)
// =============================================================================

// --- listChannelVideos ---
server.addTool({
  name: 'listChannelVideos',
  description: 'List videos from a channel. Uses search.list (100 quota units). Defaults to authenticated channel if channelId omitted. Returns video IDs and basic info.',
  parameters: ListChannelVideosParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const channelId = await resolveChannelId(yt, args.channelId);
    const res = await yt.search.list({
      part: ['snippet'],
      channelId,
      type: ['video'],
      maxResults: args.maxResults,
      pageToken: args.pageToken,
      order: args.order,
    });
    const videos = (res.data.items || []).map((item) => ({
      videoId: item.id?.videoId,
      title: item.snippet?.title,
      description: item.snippet?.description,
      publishedAt: item.snippet?.publishedAt,
      thumbnailUrl: item.snippet?.thumbnails?.default?.url,
    }));
    return JSON.stringify({
      videos,
      nextPageToken: res.data.nextPageToken,
      totalResults: res.data.pageInfo?.totalResults,
    }, null, 2);
  },
});

// --- getVideoDetails ---
server.addTool({
  name: 'getVideoDetails',
  description: 'Get full details for a video: metadata, statistics, status, content details. Only 1 quota unit — prefer this over search when you have a video ID.',
  parameters: VideoIdParameter,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const res = await yt.videos.list({
      part: ['snippet', 'contentDetails', 'statistics', 'status'],
      id: [args.videoId],
    });
    const video = res.data.items?.[0];
    if (!video) throw new UserError(`Video not found: ${args.videoId}`);
    return JSON.stringify({
      id: video.id,
      title: video.snippet?.title,
      description: video.snippet?.description,
      channelId: video.snippet?.channelId,
      channelTitle: video.snippet?.channelTitle,
      tags: video.snippet?.tags,
      categoryId: video.snippet?.categoryId,
      publishedAt: video.snippet?.publishedAt,
      duration: video.contentDetails?.duration,
      definition: video.contentDetails?.definition,
      caption: video.contentDetails?.caption,
      privacyStatus: video.status?.privacyStatus,
      uploadStatus: video.status?.uploadStatus,
      viewCount: video.statistics?.viewCount,
      likeCount: video.statistics?.likeCount,
      commentCount: video.statistics?.commentCount,
      url: `https://www.youtube.com/watch?v=${video.id}`,
    }, null, 2);
  },
});

// --- searchVideos ---
server.addTool({
  name: 'searchVideos',
  description: 'Search YouTube for videos, channels, or playlists. Uses 100 quota units per call — use sparingly. Supports filtering by channel and sorting.',
  parameters: SearchParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const params: youtube_v3.Params$Resource$Search$List = {
      part: ['snippet'],
      q: args.query,
      type: [args.type!],
      maxResults: args.maxResults,
      pageToken: args.pageToken,
      order: args.order,
    };
    if (args.channelId) {
      params.channelId = args.channelId;
    }
    const res = await yt.search.list(params);
    const results = (res.data.items || []).map((item) => ({
      id: item.id?.videoId || item.id?.channelId || item.id?.playlistId,
      kind: item.id?.kind,
      title: item.snippet?.title,
      description: item.snippet?.description,
      channelTitle: item.snippet?.channelTitle,
      publishedAt: item.snippet?.publishedAt,
      thumbnailUrl: item.snippet?.thumbnails?.default?.url,
    }));
    return JSON.stringify({
      results,
      nextPageToken: res.data.nextPageToken,
      totalResults: res.data.pageInfo?.totalResults,
    }, null, 2);
  },
});

// =============================================================================
// VIDEO METADATA & UPLOAD (6 tools)
// =============================================================================

// --- updateVideoMetadata ---
server.addTool({
  name: 'updateVideoMetadata',
  description: 'Update a video\'s title, description, tags, category, or privacy status. You must own the video. Fetches current metadata first to preserve unspecified fields.',
  parameters: VideoMetadataParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();

    // Fetch current video to preserve fields not being updated
    const current = await yt.videos.list({
      part: ['snippet', 'status'],
      id: [args.videoId],
    });
    const video = current.data.items?.[0];
    if (!video) throw new UserError(`Video not found: ${args.videoId}`);

    const snippet = video.snippet!;
    const status = video.status!;

    const res = await yt.videos.update({
      part: ['snippet', 'status'],
      requestBody: {
        id: args.videoId,
        snippet: {
          title: args.title ?? snippet.title!,
          description: args.description ?? snippet.description!,
          tags: args.tags ?? snippet.tags ?? [],
          categoryId: args.categoryId ?? snippet.categoryId!,
        },
        status: {
          privacyStatus: args.privacyStatus ?? status.privacyStatus!,
        },
      },
    });

    return JSON.stringify({
      id: res.data.id,
      title: res.data.snippet?.title,
      description: res.data.snippet?.description,
      tags: res.data.snippet?.tags,
      categoryId: res.data.snippet?.categoryId,
      privacyStatus: res.data.status?.privacyStatus,
    }, null, 2);
  },
});

// --- setVideoThumbnail ---
server.addTool({
  name: 'setVideoThumbnail',
  description: 'Upload a custom thumbnail for a video. Requires base64-encoded image data (JPEG, PNG, or BMP, max 2MB). Channel must be verified for custom thumbnails.',
  parameters: SetThumbnailParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const buffer = Buffer.from(args.imageBase64, 'base64');
    const stream = Readable.from(buffer);

    const res = await yt.thumbnails.set({
      videoId: args.videoId,
      media: {
        mimeType: args.mimeType,
        body: stream,
      },
    });

    return JSON.stringify({
      videoId: args.videoId,
      thumbnails: res.data.items?.[0],
    }, null, 2);
  },
});

// --- getVideoCategories ---
server.addTool({
  name: 'getVideoCategories',
  description: 'List available video categories for a region. Returns category IDs needed for updateVideoMetadata. Only 1 quota unit.',
  parameters: VideoCategoriesParameters,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const res = await yt.videoCategories.list({
      part: ['snippet'],
      regionCode: args.regionCode,
    });
    const categories = (res.data.items || [])
      .filter((c) => c.snippet?.assignable)
      .map((c) => ({
        id: c.id,
        title: c.snippet?.title,
      }));
    return JSON.stringify({ categories }, null, 2);
  },
});

// --- uploadVideo ---
server.addTool({
  name: 'uploadVideo',
  description: 'Upload a video file to YouTube. Defaults to private (draft) status. Supports MP4, MOV, AVI, MKV, and WebM. Optionally adds the video to a playlist after upload. Uses resumable upload — safe for large files.',
  parameters: UploadVideoParameters,
  execute: async (args, { log }) => {
    const yt = await initializeYouTubeClient();

    // Validate file exists and is readable
    if (!fs.existsSync(args.filePath)) {
      throw new UserError(`File not found: ${args.filePath}`);
    }

    const stat = fs.statSync(args.filePath);
    if (!stat.isFile()) {
      throw new UserError(`Path is not a file: ${args.filePath}`);
    }

    const ext = path.extname(args.filePath).toLowerCase();
    const mimeTypes: Record<string, string> = {
      '.mp4': 'video/mp4',
      '.mov': 'video/quicktime',
      '.avi': 'video/x-msvideo',
      '.mkv': 'video/x-matroska',
      '.webm': 'video/webm',
    };
    const mimeType = mimeTypes[ext];
    if (!mimeType) {
      throw new UserError(`Unsupported video format: ${ext}. Supported: ${Object.keys(mimeTypes).join(', ')}`);
    }

    const fileSizeMB = (stat.size / (1024 * 1024)).toFixed(1);
    log.info(`Uploading ${path.basename(args.filePath)} (${fileSizeMB} MB, ${mimeType})...`);

    const fileStream = fs.createReadStream(args.filePath);

    const res = await yt.videos.insert({
      part: ['snippet', 'status'],
      notifySubscribers: args.notifySubscribers,
      requestBody: {
        snippet: {
          title: args.title,
          description: args.description || '',
          tags: args.tags || [],
          categoryId: args.categoryId,
        },
        status: {
          privacyStatus: args.privacyStatus,
        },
      },
      media: {
        mimeType,
        body: fileStream,
      },
    });

    const videoId = res.data.id;
    const result: Record<string, unknown> = {
      videoId,
      title: res.data.snippet?.title,
      privacyStatus: res.data.status?.privacyStatus,
      uploadStatus: res.data.status?.uploadStatus,
      url: `https://www.youtube.com/watch?v=${videoId}`,
      studioUrl: `https://studio.youtube.com/video/${videoId}/edit`,
    };

    // Optionally add to playlist
    if (args.playlistId && videoId) {
      try {
        const plRes = await yt.playlistItems.insert({
          part: ['snippet'],
          requestBody: {
            snippet: {
              playlistId: args.playlistId,
              resourceId: {
                kind: 'youtube#video',
                videoId,
              },
            },
          },
        });
        result.addedToPlaylist = {
          playlistId: args.playlistId,
          playlistItemId: plRes.data.id,
        };
      } catch (playlistError: any) {
        result.playlistError = `Video uploaded but failed to add to playlist: ${playlistError.message}`;
      }
    }

    log.info(`Upload complete: ${videoId}`);
    return JSON.stringify(result, null, 2);
  },
});

// --- deleteVideo (DISABLED) ---
server.addTool({
  name: 'deleteVideo',
  description: '⛔ DISABLED FOR SAFETY — Video deletion is disabled. Delete manually via YouTube Studio.',
  parameters: VideoIdParameter,
  execute: async (args, { log }) => {
    log.warn(`deleteVideo called but is disabled. Video ID: ${args.videoId}`);
    throw new UserError(
      "🛡️ VIDEO DELETION IS DISABLED FOR SAFETY\n\n" +
      "Alternatives:\n" +
      "• Set video to 'private' using updateVideoMetadata\n" +
      "• Delete manually via YouTube Studio (studio.youtube.com)\n\n" +
      "To enable, modify the deleteVideo tool in server.ts and rebuild."
    );
  },
});

// --- getChannelInfo ---
server.addTool({
  name: 'getChannelInfo',
  description: 'Get details for the authenticated channel (or a specific channel by ID). Returns subscriber count, video count, description, and custom URL.',
  parameters: ChannelIdParameter,
  execute: async (args) => {
    const yt = await initializeYouTubeClient();
    const params: youtube_v3.Params$Resource$Channels$List = {
      part: ['snippet', 'contentDetails', 'statistics', 'status', 'brandingSettings'],
    };
    if (args.channelId) {
      params.id = [args.channelId];
    } else {
      params.mine = true;
    }
    const res = await yt.channels.list(params);
    const channel = res.data.items?.[0];
    if (!channel) throw new UserError('Channel not found');
    return JSON.stringify({
      id: channel.id,
      title: channel.snippet?.title,
      description: channel.snippet?.description,
      customUrl: channel.snippet?.customUrl,
      publishedAt: channel.snippet?.publishedAt,
      country: channel.snippet?.country,
      uploadsPlaylistId: channel.contentDetails?.relatedPlaylists?.uploads,
      subscriberCount: channel.statistics?.subscriberCount,
      videoCount: channel.statistics?.videoCount,
      viewCount: channel.statistics?.viewCount,
      keywords: channel.brandingSettings?.channel?.keywords,
      url: `https://www.youtube.com/channel/${channel.id}`,
    }, null, 2);
  },
});

// =============================================================================
// Start Server
// =============================================================================

server.start({
  transportType: 'stdio',
});

console.error('YouTube MCP Server started (stdio transport)');
