import { Heart, Star, TrendingUp, Calendar } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import type { Movie } from "./MovieCard";

interface User {
  id: string;
  name: string;
  email: string;
  joinDate: string;
  isFlagged: boolean;
  penalties: number;
  flagReason?: string;
  isAdmin: boolean;
}

interface Review {
  id: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

interface UserDashboardProps {
  currentUser: User;
  movies: Movie[];
  watchlist: string[];
  reviews: Review[];
}

export function UserDashboard({ currentUser, movies, watchlist, reviews }: UserDashboardProps) {
  const userReviews = reviews.filter((r) => r.userId === currentUser.id);
  const watchlistMovies = movies.filter((m) => watchlist.includes(m.id));
  
  const averageUserRating = userReviews.length > 0
    ? (userReviews.reduce((sum, r) => sum + r.rating, 0) / userReviews.length).toFixed(1)
    : "N/A";

  const favoriteGenres = watchlistMovies
    .flatMap((m) => m.genre)
    .reduce((acc, genre) => {
      acc[genre] = (acc[genre] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

  const topGenres = Object.entries(favoriteGenres)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([genre]) => genre);

  const joinedDaysAgo = Math.floor(
    (new Date().getTime() - new Date(currentUser.joinDate).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className="space-y-6 mb-8">
      <div>
        <h2 className="text-2xl mb-1">Welcome back, {currentUser.name}!</h2>
        <p className="text-neutral-400">Here's your movie activity</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Watchlist</CardTitle>
            <Heart className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{watchlist.length}</div>
            <p className="text-xs text-neutral-400 mt-1">
              movies saved
            </p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Reviews Written</CardTitle>
            <Star className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{userReviews.length}</div>
            <p className="text-xs text-neutral-400 mt-1">
              total reviews
            </p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Average Rating</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{averageUserRating}</div>
            <p className="text-xs text-neutral-400 mt-1">
              your avg score
            </p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Member Since</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{joinedDaysAgo}</div>
            <p className="text-xs text-neutral-400 mt-1">
              days ago
            </p>
          </CardContent>
        </Card>
      </div>

      {topGenres.length > 0 && (
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="text-sm">Your Favorite Genres</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 flex-wrap">
              {topGenres.map((genre) => (
                <Badge
                  key={genre}
                  variant="outline"
                  className="border-neutral-700 text-sm"
                >
                  {genre}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {userReviews.length > 0 && (
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="text-sm">Recent Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {userReviews.slice(0, 3).map((review, index) => {
                const movie = movies.find((m) => m.id === review.id);
                return (
                  <div key={index} className="flex items-start gap-3 pb-3 border-b border-neutral-800 last:border-0 last:pb-0">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm">{movie?.title || "Unknown"}</span>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                          <span className="text-xs text-neutral-400">{review.rating}/10</span>
                        </div>
                      </div>
                      <p className="text-xs text-neutral-400 line-clamp-2">{review.comment}</p>
                    </div>
                    <span className="text-xs text-neutral-500">{review.date}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
