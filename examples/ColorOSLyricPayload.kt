package com.aman.auramusic.coloros

import org.json.JSONArray
import org.json.JSONObject

/**
 * Utility for formatting synchronized lyrics for native ColorOS / OxygenOS / Realme UI
 * MediaSession integration.
 *
 * ColorOS SystemUI consumes this JSON payload via:
 * MediaMetadata.getString("lyricInfo")
 */
data class LyricLine(
    val timestampMs: Long,
    val text: String
)

object ColorOSLyricPayload {

    /**
     * Converts a millisecond timestamp to standard LRC format [mm:ss.xx]
     */
    fun formatTimestamp(ms: Long): String {
        val totalSeconds = ms / 1000
        val minutes = totalSeconds / 60
        val seconds = totalSeconds % 60
        val hundredths = (ms % 1000) / 10
        return String.format("[%02d:%02d.%02d]", minutes, seconds, hundredths)
    }

    /**
     * Generates the lyricInfo JSON required by ColorOS SystemUI.
     *
     * @param songTitle Name of the track
     * @param artist Artist name
     * @param songId Unique song identifier (or URI string)
     * @param lyrics List of timestamped lyric lines
     * @return Formatted JSON string ready to pass into MediaMetadata
     */
    fun generateLyricInfoJson(
        songTitle: String,
        artist: String,
        songId: String,
        lyrics: List<LyricLine>
    ): String {
        if (lyrics.isEmpty()) return ""

        val lrcBuilder = StringBuilder()
        for (line in lyrics) {
            lrcBuilder.append(formatTimestamp(line.timestampMs))
            lrcBuilder.append(line.text)
            lrcBuilder.append("\n")
        }

        val json = JSONObject()
        json.put("songName", songTitle)
        json.put("artist", artist)
        json.put("songId", songId)
        json.put("lyric", lrcBuilder.toString())

        return json.toString()
    }
}
