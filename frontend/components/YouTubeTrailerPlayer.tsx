import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    YT?: any;
    onYouTubeIframeAPIReady?: () => void;
  }
}

// Hook to load the IFrame API once and tell us when it's ready
function useYouTubeIframeAPI(): boolean {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // If already loaded, just use it
    if (window.YT && window.YT.Player) {
      setReady(true);
      return;
    }

    // If script already injected, just wait for callback
    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[src="https://www.youtube.com/iframe_api"]'
    );

    const handleReady = () => setReady(true);

    // Chain any existing callback so we don't clobber it
    const prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      prev?.();
      handleReady();
    };

    if (!existingScript) {
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      document.head.appendChild(tag);
    }

    // we don't remove the script; it's global for the app lifetime
  }, []);

  return ready;
}

interface YouTubeTrailerPlayerProps {
  videoId: string; // YouTube video id
}

export function YouTubeTrailerPlayer({ videoId }: YouTubeTrailerPlayerProps) {
  const apiReady = useYouTubeIframeAPI();
  const containerRef = useRef<HTMLDivElement | null>(null);
const playerRef = useRef<any | null>(null);

  useEffect(() => {
    if (!apiReady || !containerRef.current) return;

    // If player already exists, just load new video
    if (playerRef.current) {
      playerRef.current.loadVideoById(videoId);
      return;
    }

    playerRef.current = new window.YT!.Player(containerRef.current, {
      videoId,
      width: "100%",
      height: "100%",
      playerVars: {
        rel: 0,
        modestbranding: 1,
      },
    });

    return () => {
      playerRef.current?.destroy();
      playerRef.current = null;
    };
  }, [apiReady, videoId]);

  return (
    <div className="aspect-video w-full rounded-lg overflow-hidden bg-black">
      <div ref={containerRef} />
    </div>
  );
}
