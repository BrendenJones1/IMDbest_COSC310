import React from "react";
import { Star, Plus, Check, X } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export interface Movie {
  id: string;
  title: string;
  year: number;
  rating: number;
  poster: string;
  genre: string[];
  description: string;
  ageRating: string;
  trailerYoutubeId?: string;
  durationMinutes?: number;
  userReviews?: number;
  ratingCount?: number;
  imdbRating?: number;
}

interface MovieCardProps {
  movie: Movie;
  isInWatchlist: boolean;
  onWatchlistToggle: (movieId: string) => void;
  onMovieClick: (movie: Movie) => void;
}

export function MovieCard({ movie, isInWatchlist, onWatchlistToggle, onMovieClick }: MovieCardProps) {
  const displayRating = movie.rating && movie.rating > 0 ? movie.rating : movie.imdbRating ?? 0;
  const displayDuration =
    typeof movie.durationMinutes === "number" && movie.durationMinutes > 0
      ? `${Math.floor(movie.durationMinutes / 60)}h${movie.durationMinutes % 60 ? ` ${movie.durationMinutes % 60}m` : ""}`
      : null;
  // hide reviews per request; keep duration & rating visible

  return (
    <div className="group relative cursor-pointer" onClick={() => onMovieClick(movie)}>
      <div className="relative overflow-hidden rounded-lg aspect-[2/3] bg-neutral-800">
        <ImageWithFallback
          src={movie.poster}
          alt={movie.title}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute top-2 left-2 flex gap-2">
          {displayDuration && (
            <Badge className="bg-neutral-900/80 text-white border border-neutral-700">
              {displayDuration}
            </Badge>
          )}
          {movie.ageRating && movie.ageRating !== "NR" && (
            <Badge className="bg-yellow-500 text-black hover:bg-yellow-600">
              {movie.ageRating}
            </Badge>
          )}
        </div>
        <div className="absolute top-2 right-2">
          <Button
            size="icon"
            variant={isInWatchlist ? "default" : "secondary"}
            className={`h-8 w-8 rounded-full group/watch-btn transition-colors ${
              isInWatchlist ? "bg-green-600 hover:bg-red-600" : ""
            }`}
              onClick={(e) => {
                e.stopPropagation();
                onWatchlistToggle(movie.id);
              }}
          >
            {isInWatchlist ? (
              <span className="relative flex items-center justify-center">
                <Check className="h-4 w-4 transition-opacity group-hover/watch-btn:opacity-0" />
                <X className="h-4 w-4 text-red-200 absolute opacity-0 transition-opacity group-hover/watch-btn:opacity-100" />
              </span>
            ) : (
              <Plus className="h-4 w-4" />
            )}
          </Button>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4">
          <h3 className="text-white mb-1">{movie.title}</h3>
          <div className="flex items-center gap-3 flex-wrap text-sm">
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
              <span className="text-yellow-500">{displayRating.toFixed(1)}</span>
            </div>
            <span className="text-neutral-400">{movie.year}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
