import { Users, Flag, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Movie } from "./MovieCard";

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
  id: number;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

interface UserWatchlist {
  [userId: string]: number[];
}

interface AdminDashboardProps {
  users: User[];
  movies: Movie[];
  reviews: Review[];
  watchlists: UserWatchlist;
}

export function AdminDashboard({ users, movies, reviews, watchlists }: AdminDashboardProps) {
  const flaggedUsers = users.filter((u) => u.isFlagged);
  const totalPenalties = users.reduce((sum, u) => sum + u.penalties, 0);
  const usersWithPenalties = users.filter((u) => u.penalties > 0);

  // Get most active users
  const userActivity = users.map((user) => ({
    user,
    reviewCount: reviews.filter((r) => r.userId === user.id).length,
    watchlistCount: watchlists[user.id]?.length || 0,
    totalActivity: reviews.filter((r) => r.userId === user.id).length + (watchlists[user.id]?.length || 0),
  })).sort((a, b) => b.totalActivity - a.totalActivity).slice(0, 5);

  // Get most reviewed movies
  const movieReviewCounts = movies.map((movie) => ({
    movie,
    reviewCount: reviews.filter((r) => r.id === movie.id).length,
  })).sort((a, b) => b.reviewCount - a.reviewCount).slice(0, 5);

  return (
    <div className="space-y-6 mb-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Total Users</CardTitle>
            <Users className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{users.length}</div>
            <p className="text-xs text-neutral-400 mt-1">
              {users.filter((u) => !u.isFlagged).length} active
            </p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Flagged Users</CardTitle>
            <Flag className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{flaggedUsers.length}</div>
            {flaggedUsers.length > 0 && (
              <p className="text-xs text-red-400 mt-1">
                Requires attention
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Active Penalties</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{totalPenalties}</div>
            <p className="text-xs text-neutral-400 mt-1">
              {usersWithPenalties.length} users affected
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Most Active Users */}
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="text-sm">Most Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {userActivity.map(({ user, reviewCount, watchlistCount, totalActivity }) => (
                <div key={user.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
                      <span className="text-xs">{user.name.charAt(0)}</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{user.name}</span>
                        {user.isFlagged && (
                          <Badge variant="destructive" className="text-xs h-4 px-1">
                            <Flag className="h-2 w-2" />
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-neutral-400">
                        <span>{reviewCount} reviews</span>
                        <span>•</span>
                        <span>{watchlistCount} saved</span>
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline" className="border-neutral-700">
                    {totalActivity}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Most Reviewed Movies */}
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="text-sm">Most Reviewed Movies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {movieReviewCounts.map(({ movie, reviewCount }) => {
                const maxReviews = movieReviewCounts[0]?.reviewCount || 1;
                const percentage = (reviewCount / maxReviews) * 100;
                
                return (
                  <div key={movie.id}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm truncate flex-1">{movie.title}</span>
                      <Badge variant="outline" className="border-neutral-700 ml-2">
                        {reviewCount}
                      </Badge>
                    </div>
                    <Progress value={percentage} className="h-1.5" />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
