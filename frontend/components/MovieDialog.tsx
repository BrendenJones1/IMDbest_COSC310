import { Star, Calendar, Plus, Check } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { useState } from "react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface Movie {
  id: number;
  title: string;
  year: number;
  rating: number;
  poster: string;
  genre: string[];
  description: string;
  ageRating: string;
}

interface Review {
  id: number;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

interface MovieDialogProps {
  movie: Movie | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isInWatchlist: boolean;
  onWatchlistToggle: (movieId: number) => void;
  reviews: Review[];
  onAddReview: (movieId: number, rating: number, comment: string) => void;
}

export function MovieDialog({
  movie,
  open,
  onOpenChange,
  isInWatchlist,
  onWatchlistToggle,
  reviews,
  onAddReview
}: MovieDialogProps) {
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState("");

  if (!movie) return null;

  const handleSubmitReview = () => {
    if (newComment.trim()) {
      onAddReview(movie.id, newRating, newComment);
      setNewComment("");
      setNewRating(5);
    }
  };

  const movieReviews = reviews.filter((r) => r.id === movie.id);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-neutral-900 text-white border-neutral-800">
        <DialogHeader>
          <div className="flex gap-6">
            <div className="w-48 flex-shrink-0">
              <ImageWithFallback
                src={movie.poster}
                alt={movie.title}
                className="w-full rounded-lg"
              />
            </div>
            <div className="flex-1">
              <DialogTitle className="text-2xl mb-2">{movie.title}</DialogTitle>
              <DialogDescription className="text-neutral-300">
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center gap-1">
                    <Star className="h-5 w-5 fill-yellow-500 text-yellow-500" />
                    <span className="text-yellow-500">{movie.rating.toFixed(1)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>{movie.year}</span>
                  </div>
                  <Badge className="bg-yellow-500 text-black">
                    {movie.ageRating}
                  </Badge>
                </div>
                <div className="flex flex-wrap gap-2 mb-4">
                  {movie.genre.map((g) => (
                    <Badge key={g} variant="outline" className="border-neutral-700">
                      {g}
                    </Badge>
                  ))}
                </div>
                <p className="mb-4">{movie.description}</p>
                <Button
                  onClick={() => onWatchlistToggle(movie.id)}
                  variant={isInWatchlist ? "default" : "outline"}
                  className="gap-2"
                >
                  {isInWatchlist ? (
                    <>
                      <Check className="h-4 w-4" /> In Watchlist
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" /> Add to Watchlist
                    </>
                  )}
                </Button>
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-6">
          <h3 className="mb-4">Reviews</h3>
          
          <div className="bg-neutral-800 rounded-lg p-4 mb-4">
            <label className="block mb-2">Your Rating</label>
            <div className="flex gap-1 mb-4">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                <button
                  key={rating}
                  onClick={() => setNewRating(rating)}
                  className={`w-10 h-10 rounded ${
                    rating <= newRating
                      ? "bg-yellow-500 text-black"
                      : "bg-neutral-700 text-neutral-400"
                  }`}
                >
                  {rating}
                </button>
              ))}
            </div>
            <Textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write your review..."
              className="mb-2 bg-neutral-900 border-neutral-700"
            />
            <Button onClick={handleSubmitReview}>Submit Review</Button>
          </div>

          <div className="space-y-4">
            {movieReviews.map((review, index) => (
              <div key={index} className="bg-neutral-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-sm">
                      {review.userName.charAt(0).toUpperCase()}
                    </div>
                    <span>{review.userName}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                    <span className="text-yellow-500">{review.rating}/10</span>
                  </div>
                </div>
                <p className="text-neutral-300">{review.comment}</p>
                <span className="text-sm text-neutral-500">{review.date}</span>
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
