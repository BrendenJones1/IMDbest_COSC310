import { useEffect, useState } from "react";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";

const resolveApiBaseUrl = () => {
  const envUrl = (import.meta as any).env?.VITE_API_BASE_URL;
  if (envUrl && envUrl.trim()) return envUrl.trim();
  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  }
  return "http://localhost:8000";
};

const API_BASE_URL = resolveApiBaseUrl();


interface MyMovieNoteProps {
  userId: string;
  movieId: string;
}

export function MyMovieNote({ userId, movieId }: MyMovieNoteProps) {
  const [content, setContent] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle",
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load note for this user + movie
  useEffect(() => {
    if (!userId || !movieId) return;

    const controller = new AbortController();

    const loadNote = async () => {
      try {
        const res = await fetch(
          `${API_BASE_URL}/notes/${encodeURIComponent(userId)}/${encodeURIComponent(
            movieId,
          )}`,
          { signal: controller.signal },
        );

        if (!res.ok) {
          // If endpoint is missing (404) or note missing, keep empty silently
          return;
        }

        const data = await res.json();
        setContent(data.content ?? "");
      } catch {
        // Ignore load errors for now
      }
    };

    loadNote();

    return () => controller.abort();
  }, [userId, movieId]);

  const handleSave = async () => {
    if (!userId || !movieId) return;

    setStatus("saving");
    try {
      const res = await fetch(`${API_BASE_URL}/notes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          movie_id: movieId,
          content,
        }),
      });

      if (!res.ok) {
        if (res.status === 404) {
          throw new Error("Notes API is unavailable on the server (404).");
        }
        throw new Error("Failed to save note");
      }

      setStatus("saved");
      setTimeout(() => setStatus("idle"), 2000);
    } catch (e) {
      setStatus("error");
      setErrorMessage(
        e instanceof Error ? e.message : "Unable to save note right now."
      );
    }
  };

  return (
    <div className="mt-6 border-t border-neutral-800 pt-4">
      <h3 className="text-lg font-semibold mb-1">My Notes</h3>
      <p className="text-xs text-neutral-400 mb-2">
        This note is only visible to you.
      </p>
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={4}
        className="bg-neutral-900 border-neutral-700"
        placeholder="Write something about this movie..."
      />
      <div className="flex items-center gap-3 mt-2">
        <Button
          size="sm"
          className="bg-blue-600 hover:bg-blue-700"
          onClick={handleSave}
          disabled={status === "saving"}
        >
          {status === "saving" ? "Saving..." : "Save note"}
        </Button>
        {status === "saved" && (
          <span className="text-xs text-emerald-400">Saved</span>
        )}
        {status === "error" && (
          <span className="text-xs text-red-400">
            {errorMessage || "Error saving note"}
          </span>
        )}
      </div>
    </div>
  );
}
