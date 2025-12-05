import React from "react";
import { Star, Calendar, Plus, Check, Flag, ThumbsUp, ThumbsDown } from "lucide-react";
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
import { useEffect, useMemo, useState } from "react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import type { Movie } from "./MovieCard";
import { YouTubeTrailerPlayer } from "./YouTubeTrailerPlayer"; 
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogCancel,
} from "./ui/alert-dialog";

interface UserReview {
  movieId: string;
  userId: string;
  username: string;
  rating: number;
  reviewText: string;
  upvotes: number;
  downvotes: number;
  createdAt: string;
}

interface MovieDialogProps {
  movie: Movie | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isInWatchlist: boolean;
  onWatchlistToggle: (movieId: string) => void;
  reviews: UserReview[];
  onVoteReview: (movieId: string, reviewUserId: string, direction: "up" | "down") => Promise<void> | void;
  onSubmitReview: (movieId: string, rating: number, comment: string) => Promise<void> | void;
  onDeleteReview: (movieId: string, userId?: string) => Promise<void> | void;
  userReview?: UserReview;
  currentUserId: string;
  currentUserName: string;
  isAuthenticated: boolean;
  onRequireLogin?: () => void;
  reviewError?: string | null;
  isReviewLoading?: boolean;
  onFlagReview: (payload: {
    movieId: string;
    reviewUserId?: string;
    reviewUserName?: string;
    reason: string;
  }) => Promise<unknown>;
}

export function MovieDialog({
  movie,
  open,
  onOpenChange,
  isInWatchlist,
  onWatchlistToggle,
  reviews,
  onVoteReview,
  onSubmitReview,
  onDeleteReview,
  userReview,
  currentUserId,
  currentUserName,
  isAuthenticated,
  onRequireLogin,
  reviewError,
  isReviewLoading,
  onFlagReview,
}: MovieDialogProps) {
  const [flaggingReview, setFlaggingReview] = useState<UserReview | null>(null);
  const [flagReason, setFlagReason] = useState("");
  const [flagError, setFlagError] = useState<string | null>(null);
  const [flagSuccessMessage, setFlagSuccessMessage] = useState<string | null>(null);
  const [isFlagSubmitting, setIsFlagSubmitting] = useState(false);
  const [pendingVoteFor, setPendingVoteFor] = useState<string | null>(null);
  const [isReviewFormOpen, setIsReviewFormOpen] = useState(false);
  const [draftRating, setDraftRating] = useState<number>(8);
  const [draftComment, setDraftComment] = useState("");
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [reviewSubmitError, setReviewSubmitError] = useState<string | null>(null);
  const [sortMode, setSortMode] = useState<"upvotes" | "recent">("upvotes");
  const [visibleCount, setVisibleCount] = useState<number>(3);
  const [expandedReviews, setExpandedReviews] = useState<Set<string>>(new Set());

  const closeFlagDialog = () => {
    setFlaggingReview(null);
    setFlagReason("");
    setFlagError(null);
    setIsFlagSubmitting(false);
  };

  const handleFlagSubmit = async () => {
    if (!flaggingReview || !movie) return;
    if (!flagReason.trim()) {
      setFlagError("Please share a short reason.");
      return;
    }

    setIsFlagSubmitting(true);
    setFlagError(null);
    try {
      await onFlagReview({
        movieId: movie.id,
        reviewUserId: flaggingReview.userId,
        reviewUserName: flaggingReview.username,
        reason: flagReason.trim(),
      });
      setFlagSuccessMessage("Thanks! We'll review this submission shortly.");
      setTimeout(() => setFlagSuccessMessage(null), 4000);
      closeFlagDialog();
    } catch (error) {
      setFlagError(
        error instanceof Error
          ? error.message
          : "Unable to flag this review right now."
      );
    } finally {
      setIsFlagSubmitting(false);
    }
  };

  const movieId = movie?.id;

  const movieReviews = useMemo(
    () => (movieId ? reviews.filter((r) => r.movieId === movieId) : []),
    [reviews, movieId]
  );

  const sortedReviews = useMemo(() => {
    const items = [...movieReviews];
    if (sortMode === "recent") {
      items.sort((a, b) => new Date(b.createdAt || "").getTime() - new Date(a.createdAt || "").getTime());
    } else {
      items.sort((a, b) => (b.upvotes || 0) - (a.upvotes || 0));
    }
    return items;
  }, [movieReviews, sortMode]);

  useEffect(() => {
    setVisibleCount(3);
  }, [sortMode, movieId]);

  useEffect(() => {
    setVisibleCount(3);
  }, [movieId]);

  const handleVote = async (direction: "up" | "down", review: UserReview) => {
    if (!movie) return;
    if (review.userId === currentUserId) {
      return;
    }
    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }
    try {
      setPendingVoteFor(`${direction}-${review.userId}`);
      await onVoteReview(movie.id, review.userId, direction);
    } finally {
      setPendingVoteFor(null);
    }
  };

  const handleStartReview = () => {
    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }
    setIsReviewFormOpen(true);
  };

  const handleSubmitReview = async () => {
    if (!movie) return;
    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }
    setIsSubmittingReview(true);
    setReviewSubmitError(null);
    try {
      await onSubmitReview(movie.id, draftRating, draftComment);
      setIsReviewFormOpen(false);
    } catch (error) {
      setReviewSubmitError(error instanceof Error ? error.message : "Unable to save review.");
    } finally {
      setIsSubmittingReview(false);
    }
  };

  const handleDeleteReview = async () => {
    if (!movie || !userReview) return;
    try {
      await onDeleteReview(movie.id, currentUserId);
      setIsReviewFormOpen(false);
      setDraftComment("");
      setDraftRating(8);
    } catch (error) {
      setReviewSubmitError(error instanceof Error ? error.message : "Unable to delete review.");
    }
  };

  useEffect(() => {
    if (userReview) {
      setDraftRating(userReview.rating || 8);
      setDraftComment(userReview.reviewText || "");
      setIsReviewFormOpen(true);
    } else {
      setDraftRating(8);
      setDraftComment("");
      setIsReviewFormOpen(false);
    }
  }, [userReview]);

  useEffect(() => {
    setVisibleCount(3);
  }, [movieId]);

  if (!movie) return null;

  const ratingValue = typeof movie.rating === "number" ? movie.rating : Number(movie.rating ?? 0);
  const ratingDisplay = Number.isFinite(ratingValue) ? ratingValue.toFixed(1) : "0.0";
  const movieGenres = Array.isArray(movie.genre) ? movie.genre : [];

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
              <div className="text-neutral-300">
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center gap-1">
                    <Star className="h-5 w-5 fill-yellow-500 text-yellow-500" />
                    <span className="text-yellow-500">{ratingDisplay}</span>
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
                  {movieGenres.map((g) => (
                    <Badge key={g} variant="outline" className="border-neutral-700">
                      {g}
                    </Badge>
                  ))}
                </div>
                <div className="mb-4 text-neutral-300">{movie.description}</div>
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
              </div>
            </div>
          </div>
          {movie.trailerYoutubeId && (
            <div className="mt-2">
              <h3 className="mb-2 text-lg font-semibold">Trailer</h3>
              <YouTubeTrailerPlayer videoId={movie.trailerYoutubeId} />
            </div>
          )}
        </DialogHeader>

        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Reviews</h3>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2">
                <Button
                  variant={sortMode === "recent" ? "default" : "secondary"}
                  size="sm"
                  onClick={() => setSortMode("recent")}
                >
                  Recent
                </Button>
                <Button
                  variant={sortMode === "upvotes" ? "default" : "secondary"}
                  size="sm"
                  onClick={() => setSortMode("upvotes")}
                >
                  Most Upvotes
                </Button>
              </div>
              <Button variant="secondary" size="sm" onClick={handleStartReview}>
                + Review
              </Button>
            </div>
          </div>
          {flagSuccessMessage && (
            <div className="mb-4 rounded-lg border border-green-700 bg-green-900/40 px-4 py-2 text-sm text-green-200">
              {flagSuccessMessage}
            </div>
          )}
          {reviewError && (
            <div className="mb-4 rounded-lg border border-red-800 bg-red-900/40 px-4 py-2 text-sm text-red-200">
              {reviewError}
            </div>
          )}

          {isReviewFormOpen && (
            <div className="mb-6 bg-neutral-800 rounded-lg p-4 border border-neutral-700">
              <h4 className="font-semibold mb-3">{userReview ? "Edit your review" : "Write a review"}</h4>
              <div className="mb-3">
                <label className="block text-sm text-neutral-300 mb-1">Your rating</label>
                <div className="flex gap-1">
                  {Array.from({ length: 10 }, (_, i) => i + 1).map((value) => {
                    const active = value <= draftRating;
                    return (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setDraftRating(value)}
                        className="w-9 h-9 flex items-center justify-center"
                      >
                        <Star
                          className={`h-5 w-5 ${
                            active
                              ? "fill-yellow-500 stroke-yellow-500 text-yellow-500"
                              : "fill-transparent stroke-yellow-500 text-yellow-500"
                          }`}
                        />
                      </button>
                    );
                  })}
                </div>
              </div>
              <div className="mb-3">
                <label className="block text-sm text-neutral-300 mb-1">Your review</label>
                <Textarea
                  value={draftComment}
                  onChange={(e) => setDraftComment(e.target.value)}
                  placeholder="Share your thoughts..."
                  className="bg-neutral-900 border-neutral-700"
                  rows={4}
                />
              </div>
              {reviewSubmitError && (
                <div className="mb-3 text-sm text-red-400">{reviewSubmitError}</div>
              )}
              <div className="flex items-center gap-3">
                <Button onClick={handleSubmitReview} disabled={isSubmittingReview}>
                  {isSubmittingReview ? "Saving..." : "Save review"}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setIsReviewFormOpen(false)}
                  disabled={isSubmittingReview}
                >
                  Cancel
                </Button>
                {userReview && (
                  <Button
                    variant="destructive"
                    onClick={handleDeleteReview}
                    disabled={isSubmittingReview}
                  >
                    Delete review
                  </Button>
                )}
              </div>
            </div>
          )}

          {isReviewLoading ? (
            <div className="text-neutral-400">Loading reviews…</div>
          ) : sortedReviews.length === 0 ? (
            <div className="text-neutral-400">No reviews yet.</div>
          ) : (
            <div className="space-y-4">
              {sortedReviews.slice(0, visibleCount).map((review) => (
                <div key={`${review.userId}-${review.createdAt}`} className="bg-neutral-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-sm">
                        {(review.username || review.userId || "?").charAt(0).toUpperCase()}
                      </div>
                      <div className="flex flex-col">
                        <span>{review.username || review.userId}</span>
                        <span className="text-xs text-neutral-500">
                          {review.createdAt ? new Date(review.createdAt).toLocaleDateString() : ""}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                        <span className="text-yellow-500">{review.rating}/10</span>
                      </div>
                      {review.username !== currentUserName && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 px-2 text-xs text-red-400 hover:text-red-200"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            setFlaggingReview(review);
                            setFlagReason("");
                            setFlagError(null);
                          }}
                        >
                          <Flag className="h-3.5 w-3.5 mr-1" />
                          Flag
                        </Button>
                      )}
                    </div>
                  </div>
                  <p className="text-neutral-300 whitespace-pre-line">
                    {expandedReviews.has(review.userId)
                      ? review.reviewText
                      : (() => {
                          const lines = review.reviewText.split("\n");
                          if (lines.length <= 5) return review.reviewText;
                          return lines.slice(0, 5).join("\n") + "\n...";
                        })()}
                  </p>
                  {review.reviewText.split("\n").length > 5 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="px-2 text-xs text-yellow-500 hover:text-yellow-300"
                      onClick={() => {
                        setExpandedReviews((prev) => {
                          const next = new Set(prev);
                          if (next.has(review.userId)) {
                            next.delete(review.userId);
                          } else {
                            next.add(review.userId);
                          }
                          return next;
                        });
                      }}
                    >
                      {expandedReviews.has(review.userId) ? "Show less" : "Show more"}
                    </Button>
                  )}
                  <div className="mt-3 flex items-center gap-3 text-sm text-neutral-300">
                    <Button
                      variant="secondary"
                      size="sm"
                      className="h-8"
                      disabled={pendingVoteFor === `up-${review.userId}` || review.userId === currentUserId}
                      onClick={() => handleVote("up", review)}
                    >
                      <ThumbsUp className="h-4 w-4 mr-1" />
                      {review.upvotes}
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      className="h-8"
                      disabled={pendingVoteFor === `down-${review.userId}` || review.userId === currentUserId}
                      onClick={() => handleVote("down", review)}
                    >
                      <ThumbsDown className="h-4 w-4 mr-1" />
                      {review.downvotes}
                    </Button>
                  </div>
                </div>
              ))}
              {visibleCount < sortedReviews.length && (
                <div className="flex justify-center">
                  <Button
                    variant="secondary"
                    onClick={() => setVisibleCount((v) => Math.min(sortedReviews.length, v + 3))}
                  >
                    Show more
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </DialogContent>

      <AlertDialog open={Boolean(flaggingReview)} onOpenChange={(open) => {
        if (!open) {
          closeFlagDialog();
        }
      }}>
        <AlertDialogContent className="bg-neutral-900 border-neutral-800 text-white">
          <AlertDialogHeader>
            <AlertDialogTitle>Flag Review</AlertDialogTitle>
            <AlertDialogDescription className="text-neutral-300">
              Tell us why the review from {flaggingReview?.username || "this user"} for "{movie.title}" should be moderated.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Textarea
            value={flagReason}
            onChange={(e) => setFlagReason(e.target.value)}
            placeholder="e.g., Contains spoilers, spam, harassment..."
            className="bg-neutral-800 border-neutral-700"
          />
          {flagError && <p className="text-sm text-red-400">{flagError}</p>}
          <AlertDialogFooter className="gap-2">
            <AlertDialogCancel className="bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
              Cancel
            </AlertDialogCancel>
            <Button
              className="bg-red-600 hover:bg-red-700"
              onClick={handleFlagSubmit}
              disabled={isFlagSubmitting}
            >
              {isFlagSubmitting ? "Submitting..." : "Submit Flag"}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Dialog>
  );
}
