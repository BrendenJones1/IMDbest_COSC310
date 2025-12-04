import { Star, Plus, Check } from "lucide-react";
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
}

interface MovieCardProps {
  movie: Movie;
  isInWatchlist: boolean;
  onWatchlistToggle: (movieId: string) => void;
  onMovieClick: (movie: Movie) => void;
}

export function MovieCard({ movie, isInWatchlist, onWatchlistToggle, onMovieClick }: MovieCardProps) {
  return (
    <div className="group relative cursor-pointer" onClick={() => onMovieClick(movie)}>
      <div className="relative overflow-hidden rounded-lg aspect-[2/3] bg-neutral-800">
        <ImageWithFallback
          src={movie.poster}
          alt={movie.title}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute top-2 left-2">
          <Badge className="bg-yellow-500 text-black hover:bg-yellow-600">
            {movie.ageRating}
          </Badge>
        </div>
        <div className="absolute top-2 right-2">
          <Button
            size="icon"
            variant={isInWatchlist ? "default" : "secondary"}
            className="h-8 w-8 rounded-full"
              onClick={(e) => {
                e.stopPropagation();
                onWatchlistToggle(movie.id);
              }}
          >
            {isInWatchlist ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          </Button>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4">
          <h3 className="text-white mb-1">{movie.title}</h3>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
              <span className="text-yellow-500">{movie.rating.toFixed(1)}</span>
            </div>
            <span className="text-neutral-400">{movie.year}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
