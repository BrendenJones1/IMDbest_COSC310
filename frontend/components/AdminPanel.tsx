import { useState } from "react";
import { Trash2, Plus, Star, Shield, MinusCircle, Flag, AlertTriangle, Users as UsersIcon, Film as FilmIcon, MessageSquare } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";
import { Badge } from "./ui/badge";
import { Movie } from "./MovieCard";

interface Review {
  id: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

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

interface UserWatchlist {
  [userId: string]: string[];
}

interface AdminPanelProps {
  movies: Movie[];
  users: User[];
  reviews: Review[];
  watchlists: UserWatchlist;
  onDeleteMovie: (movieId: string) => void;
  onEditMovie: (movie: Movie) => void;
  onAddMovie: (movie: Omit<Movie, "id">) => void;
  onDeleteReview: (movieId: string, userId: string, date: string) => void;
  onDeleteUser: (userId: string) => void;
  onFlagUser: (userId: string, reason: string) => void;
  onUnflagUser: (userId: string) => void;
  onAddPenalty: (userId: string) => void;
  onRemovePenalty: (userId: string) => void;
}

export function AdminPanel({
  movies,
  users,
  reviews,
  watchlists,
  onDeleteMovie,
  onEditMovie,
  onAddMovie,
  onDeleteReview,
  onDeleteUser,
  onFlagUser,
  onUnflagUser,
  onAddPenalty,
  onRemovePenalty,
}: AdminPanelProps) {
  const [isAddMovieOpen, setIsAddMovieOpen] = useState(false);
  const [editingMovie, setEditingMovie] = useState<Movie | null>(null);
  const [flaggingUser, setFlaggingUser] = useState<User | null>(null);
  const [flagReason, setFlagReason] = useState("");
  const [newMovie, setNewMovie] = useState({
    title: "",
    year: 2024,
    rating: 7.0,
    poster: "",
    genre: "",
    description: "",
    ageRating: "PG-13",
  });

  const flaggedUsers = users.filter((u) => u.isFlagged);
  const usersWithPenalties = users.filter((u) => u.penalties > 0);

  const handleAddMovie = () => {
    if (newMovie.title) {
      const movieToAdd: Omit<Movie, "id"> = {
        ...newMovie,
        genre: newMovie.genre.split(",").map((g) => g.trim()).filter(Boolean),
        poster: newMovie.poster,
      };
      onAddMovie(movieToAdd);
      setNewMovie({
        title: "",
        year: 2024,
        rating: 7.0,
        poster: "",
        genre: "",
        description: "",
        ageRating: "PG-13",
      });
      setIsAddMovieOpen(false);
    }
  };

  const handleEditMovie = () => {
    if (editingMovie) {
      onEditMovie(editingMovie);
      setEditingMovie(null);
    }
  };

  const handleFlagUser = () => {
    if (flaggingUser && flagReason.trim()) {
      onFlagUser(flaggingUser.id, flagReason);
      setFlaggingUser(null);
      setFlagReason("");
    }
  };

  return (
    <div className="space-y-6 text-white">
      <div>
        <h1 className="text-3xl mb-2">Admin Panel</h1>
        <p className="text-neutral-300">Comprehensive management for movies, users, reviews, flags, and penalties</p>
      </div>

      <Tabs defaultValue="movies" className="w-full">
        <TabsList className="bg-neutral-900 border-neutral-800 text-white">
          <TabsTrigger value="movies" className="gap-2 text-white data-[state=active]:text-black">
            <FilmIcon className="h-4 w-4" />
            Movies
          </TabsTrigger>
          <TabsTrigger value="users" className="gap-2 text-white data-[state=active]:text-black">
            <UsersIcon className="h-4 w-4" />
            Users
          </TabsTrigger>
          <TabsTrigger value="reviews" className="gap-2 text-white data-[state=active]:text-black">
            <MessageSquare className="h-4 w-4" />
            Reviews
          </TabsTrigger>
          <TabsTrigger value="flags" className="gap-2 text-white data-[state=active]:text-black">
            <Flag className="h-4 w-4" />
            Flags & Penalties
          </TabsTrigger>
        </TabsList>

        {/* Movies Management */}
        <TabsContent value="movies" className="space-y-4">
          <Card className="bg-neutral-900 border-neutral-800 text-white">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Movie Management</CardTitle>
                  <p className="text-sm text-neutral-300 mt-1">{movies.length} total movies</p>
                </div>
                <Dialog open={isAddMovieOpen} onOpenChange={setIsAddMovieOpen}>
                  <DialogTrigger asChild>
                    <Button className="gap-2">
                      <Plus className="h-4 w-4" />
                      Add Movie
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-neutral-900 border-neutral-800 text-white">
                    <DialogHeader>
                      <DialogTitle>Add New Movie</DialogTitle>
                      <DialogDescription className="text-neutral-300">
                        Add a new movie to the database
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label>Title</Label>
                        <Input
                          value={newMovie.title}
                          onChange={(e) =>
                            setNewMovie({ ...newMovie, title: e.target.value })
                          }
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Year</Label>
                          <Input
                            type="number"
                            value={newMovie.year}
                            onChange={(e) =>
                              setNewMovie({ ...newMovie, year: parseInt(e.target.value) })
                            }
                            className="bg-neutral-800 border-neutral-700"
                          />
                        </div>
                        <div>
                          <Label>Rating</Label>
                          <Input
                            type="number"
                            step="0.1"
                            value={newMovie.rating}
                            onChange={(e) =>
                              setNewMovie({ ...newMovie, rating: parseFloat(e.target.value) })
                            }
                            className="bg-neutral-800 border-neutral-700"
                          />
                        </div>
                      </div>
                      <div>
                        <Label>Poster URL</Label>
                        <Input
                          value={newMovie.poster}
                          onChange={(e) =>
                            setNewMovie({ ...newMovie, poster: e.target.value })
                          }
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <div>
                        <Label>Genre (comma separated)</Label>
                        <Input
                          value={newMovie.genre}
                          onChange={(e) =>
                            setNewMovie({ ...newMovie, genre: e.target.value })
                          }
                          placeholder="Action, Thriller"
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <div>
                        <Label>Age Rating</Label>
                        <Input
                          value={newMovie.ageRating}
                          onChange={(e) =>
                            setNewMovie({ ...newMovie, ageRating: e.target.value })
                          }
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <div>
                        <Label>Description</Label>
                        <Textarea
                          value={newMovie.description}
                          onChange={(e) =>
                            setNewMovie({ ...newMovie, description: e.target.value })
                          }
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <Button onClick={handleAddMovie} className="w-full">
                        Add Movie
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table className="text-white">
                <TableHeader>
                  <TableRow className="border-neutral-800 text-neutral-200">
                    <TableHead className="text-neutral-200">Title</TableHead>
                    <TableHead className="text-neutral-200">Year</TableHead>
                    <TableHead className="text-neutral-200">Rating</TableHead>
                    <TableHead className="text-neutral-200">Genre</TableHead>
                    <TableHead className="text-neutral-200">Reviews</TableHead>
                    <TableHead className="text-neutral-200 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {movies.map((movie) => {
                    const reviewCount = reviews.filter((r) => r.id === movie.id).length;
                    return (
                      <TableRow key={movie.id} className="border-neutral-800 text-white/90">
                        <TableCell>{movie.title}</TableCell>
                        <TableCell>{movie.year}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                            {movie.rating}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1 flex-wrap">
                            {movie.genre.map((g) => (
                              <Badge
                                key={g}
                                variant="outline"
                                className="border-neutral-700 text-xs"
                              >
                                {g}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-neutral-700">
                            {reviewCount}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-red-500 hover:text-red-400"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent className="bg-neutral-900 border-neutral-800 text-white">
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Movie</AlertDialogTitle>
                                <AlertDialogDescription className="text-neutral-300">
                                  Are you sure you want to delete "{movie.title}"? This will permanently remove the movie and all its associated reviews. This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel className="bg-neutral-800 border-neutral-700">
                                  Cancel
                                </AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => onDeleteMovie(movie.id)}
                                  className="bg-red-600 hover:bg-red-700"
                                >
                                  Delete Movie
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Users Management */}
        <TabsContent value="users" className="space-y-4">
          <Card className="bg-neutral-900 border-neutral-800 text-white">
            <CardHeader>
              <div>
                <CardTitle>User Management</CardTitle>
                <p className="text-sm text-neutral-300 mt-1">
                  {users.length} total users • {flaggedUsers.length} flagged • {usersWithPenalties.length} with penalties
                </p>
              </div>
            </CardHeader>
            <CardContent>
              <Table className="text-white">
                <TableHeader>
                  <TableRow className="border-neutral-800 text-neutral-200">
                    <TableHead className="text-neutral-200">Username</TableHead>
                    <TableHead className="text-neutral-200">Email</TableHead>
                    <TableHead className="text-neutral-200">Status</TableHead>
                    <TableHead className="text-neutral-200">Penalties</TableHead>
                    <TableHead className="text-neutral-200">Watchlist</TableHead>
                    <TableHead className="text-neutral-200">Reviews</TableHead>
                    <TableHead className="text-neutral-200 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id} className="border-neutral-800 text-white/90">
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {user.name}
                          {user.isAdmin && (
                            <Badge variant="outline" className="border-blue-800 text-blue-400 gap-1">
                              <Shield className="h-3 w-3" />
                              Admin
                            </Badge>
                          )}
                          {user.isFlagged && (
                            <Badge variant="destructive" className="gap-1">
                              <Flag className="h-3 w-3" />
                              Flagged
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-neutral-200">{user.email}</TableCell>
                      <TableCell>
                        {user.isFlagged ? (
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="border-red-800 text-red-400">
                              {user.flagReason || "Flagged"}
                            </Badge>
                          </div>
                        ) : (
                          <Badge variant="outline" className="border-green-800 text-green-400">
                            Active
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {user.penalties > 0 ? (
                            <Badge variant="outline" className="border-yellow-800 text-yellow-400 gap-1">
                              <AlertTriangle className="h-3 w-3" />
                              {user.penalties}
                            </Badge>
                          ) : (
                            <span className="text-neutral-300">None</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{watchlists[user.id]?.length || 0}</TableCell>
                      <TableCell>
                        {reviews.filter((r) => r.userId === user.id).length}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          {user.isFlagged ? (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-green-500 hover:text-green-400"
                              onClick={() => onUnflagUser(user.id)}
                              title="Unflag user"
                            >
                              <Shield className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Dialog 
                              open={flaggingUser?.id === user.id} 
                              onOpenChange={(open) => {
                                if (!open) {
                                  setFlaggingUser(null);
                                  setFlagReason("");
                                }
                              }}
                            >
                              <DialogTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-yellow-500 hover:text-yellow-400"
                                  onClick={() => setFlaggingUser(user)}
                                  title="Flag user"
                                >
                                  <Flag className="h-4 w-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="bg-neutral-900 border-neutral-800 text-white">
                                <DialogHeader>
                                  <DialogTitle>Flag User</DialogTitle>
                                  <DialogDescription className="text-neutral-300">
                                    Flag {user.name} for policy violations
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <Label>Reason for flagging</Label>
                                    <Textarea
                                      value={flagReason}
                                      onChange={(e) => setFlagReason(e.target.value)}
                                      placeholder="e.g., Spam reviews, inappropriate content..."
                                      className="bg-neutral-800 border-neutral-700"
                                    />
                                  </div>
                                  <Button onClick={handleFlagUser} className="w-full">
                                    Flag User
                                  </Button>
                                </div>
                              </DialogContent>
                            </Dialog>
                          )}
                          
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-orange-500 hover:text-orange-400"
                            onClick={() => onAddPenalty(user.id)}
                            title="Add penalty"
                          >
                            <Plus className="h-4 w-4" />
                          </Button>
                          
                          {user.penalties > 0 && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-blue-500 hover:text-blue-400"
                              onClick={() => onRemovePenalty(user.id)}
                              title="Remove penalty"
                            >
                              <MinusCircle className="h-4 w-4" />
                            </Button>
                          )}
                          
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-red-500 hover:text-red-400"
                                title="Delete user"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent className="bg-neutral-900 border-neutral-800 text-white">
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete User Account</AlertDialogTitle>
                                <AlertDialogDescription className="text-neutral-300">
                                  Are you sure you want to delete {user.name}'s account? This will permanently remove their watchlist, reviews, and all associated data. This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel className="bg-neutral-800 border-neutral-700">
                                  Cancel
                                </AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => onDeleteUser(user.id)}
                                  className="bg-red-600 hover:bg-red-700"
                                >
                                  Delete User
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reviews Management */}
        <TabsContent value="reviews" className="space-y-4">
          <Card className="bg-neutral-900 border-neutral-800 text-white">
            <CardHeader>
              <div>
                <CardTitle>Reviews Management</CardTitle>
                <p className="text-sm text-neutral-300 mt-1">{reviews.length} total reviews</p>
              </div>
            </CardHeader>
            <CardContent>
              <Table className="text-white">
                <TableHeader>
                  <TableRow className="border-neutral-800 text-neutral-200">
                    <TableHead className="text-neutral-200">Movie</TableHead>
                    <TableHead className="text-neutral-200">User</TableHead>
                    <TableHead className="text-neutral-200">Rating</TableHead>
                    <TableHead className="text-neutral-200">Comment</TableHead>
                    <TableHead className="text-neutral-200">Date</TableHead>
                    <TableHead className="text-neutral-200 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reviews.map((review, index) => {
                    const movie = movies.find((m) => m.id === review.id);
                    const user = users.find((u) => u.id === review.userId);
                    return (
                      <TableRow key={index} className="border-neutral-800 text-white/90">
                        <TableCell>{movie?.title || "Unknown"}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {review.userName}
                            {user?.isFlagged && (
                              <Badge variant="destructive" className="text-xs h-4 px-1">
                                <Flag className="h-2 w-2" />
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                            {review.rating}/10
                          </div>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">
                          {review.comment}
                        </TableCell>
                        <TableCell>{review.date}</TableCell>
                        <TableCell className="text-right">
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-red-500 hover:text-red-400"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent className="bg-neutral-900 border-neutral-800 text-white">
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Review</AlertDialogTitle>
                                <AlertDialogDescription className="text-neutral-300">
                                  Are you sure you want to delete this review from {review.userName}? This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel className="bg-neutral-800 border-neutral-700">
                                  Cancel
                                </AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => onDeleteReview(review.id, review.userId, review.date)}
                                  className="bg-red-600 hover:bg-red-700"
                                >
                                  Delete Review
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Flags & Penalties Management */}
        <TabsContent value="flags" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Flagged Users */}
            <Card className="bg-neutral-900 border-neutral-800 text-white">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Flag className="h-5 w-5 text-red-500" />
                  <div>
                    <CardTitle>Flagged Users</CardTitle>
                    <p className="text-sm text-neutral-300 mt-1">{flaggedUsers.length} users flagged</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {flaggedUsers.length > 0 ? (
                  <div className="space-y-3">
                    {flaggedUsers.map((user) => (
                      <div key={user.id} className="p-3 bg-neutral-800/50 rounded-lg border border-neutral-700">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span>{user.name}</span>
                              <Badge variant="destructive" className="text-xs">
                                Flagged
                              </Badge>
                            </div>
                            <p className="text-sm text-neutral-300">{user.email}</p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-green-500 hover:text-green-400"
                            onClick={() => onUnflagUser(user.id)}
                          >
                            <Shield className="h-4 w-4 mr-1" />
                            Unflag
                          </Button>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <p className="text-xs text-neutral-500 mb-1">Reason:</p>
                            <p className="text-sm">{user.flagReason}</p>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-neutral-300">
                              {reviews.filter((r) => r.userId === user.id).length} reviews • {watchlists[user.id]?.length || 0} in watchlist
                            </span>
                            {user.penalties > 0 && (
                              <Badge variant="outline" className="border-yellow-800 text-yellow-400">
                                {user.penalties} penalties
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-neutral-500">
                    <Flag className="h-12 w-12 mx-auto mb-2 opacity-30" />
                    <p>No flagged users</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Users with Penalties */}
            <Card className="bg-neutral-900 border-neutral-800 text-white">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                  <div>
                    <CardTitle>Users with Penalties</CardTitle>
                    <p className="text-sm text-neutral-300 mt-1">{usersWithPenalties.length} users with penalties</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {usersWithPenalties.length > 0 ? (
                  <div className="space-y-3">
                    {usersWithPenalties.map((user) => (
                      <div key={user.id} className="p-3 bg-neutral-800/50 rounded-lg border border-neutral-700">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span>{user.name}</span>
                              <Badge variant="outline" className="border-yellow-800 text-yellow-400 text-xs">
                                {user.penalties} {user.penalties === 1 ? "penalty" : "penalties"}
                              </Badge>
                              {user.isFlagged && (
                                <Badge variant="destructive" className="text-xs">
                                  <Flag className="h-2 w-2 mr-1" />
                                  Flagged
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-neutral-300">{user.email}</p>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-blue-500 hover:text-blue-400"
                              onClick={() => onRemovePenalty(user.id)}
                              title="Remove penalty"
                            >
                              <MinusCircle className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-orange-500 hover:text-orange-400"
                              onClick={() => onAddPenalty(user.id)}
                              title="Add penalty"
                            >
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-sm text-neutral-300">
                          <span>
                            {reviews.filter((r) => r.userId === user.id).length} reviews • {watchlists[user.id]?.length || 0} in watchlist
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-neutral-500">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-2 opacity-30" />
                    <p>No users with penalties</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
