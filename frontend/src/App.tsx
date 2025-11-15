import { useEffect, useMemo, useState } from "react";
import { backendMovies } from "./data/backendMovies";
import { fetchCurrentUser, loginRequest, registerRequest, type ApiUser, type AuthResponse } from "./api/auth";
import { Search, SlidersHorizontal, ArrowUpDown } from "lucide-react";
import { Input } from "../components/ui/input";
import { Sidebar } from "../components/Sidebar";
import { MovieCard, type Movie } from "../components/MovieCard";
import { MovieCarousel } from "../components/MovieCarousel";
import { MovieDialog } from "../components/MovieDialog";
import { AdminPanel } from "../components/AdminPanel";
import { ApiDocs } from "../components/ApiDocs";
import { UserManagement } from "../components/UserManagement";
import { UserSwitcher } from "../components/UserSwitcher";
import { UserDashboard } from "../components/UserDashboard";
import { AdminDashboard } from "../components/AdminDashboard";
import { RegisterScreen } from "../components/RegisterScreen";
import { LoginScreen } from "../components/LoginScreen";
import { Button } from "../components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "../components/ui/carousel";

const initialMovies: Movie[] = backendMovies.map((movie, index) => ({
  id: movie.id ?? index + 1,
  title: movie.title,
  year: movie.year ?? 2024,
  rating: Number(movie.rating) || 0,
  poster: movie.poster,
  genre: [...(movie.genre ?? [])],
  description: movie.description || "Description coming soon...",
  ageRating: movie.ageRating || "PG-13",
}));

const carouselSlides = backendMovies.slice(0, 3).map((movie) => ({
  id: movie.id,
  image: movie.poster,
  title: movie.title,
}));

interface User {
  id: string;
  name: string;
  email: string;
  joinDate: string;
  isFlagged: boolean;
  penalties: number;
  flagReason?: string;
  isAdmin: boolean;
  watchlistCount?: number;
  reviewCount?: number;
}

const mockUsers: User[] = [
  {
    id: "alice",
    name: "Alice",
    email: "alice@example.com",
    joinDate: "2024-01-15",
    isFlagged: false,
    penalties: 0,
    isAdmin: true,
  },
  {
    id: "bob",
    name: "Bob",
    email: "bob@example.com",
    joinDate: "2024-02-20",
    isFlagged: false,
    penalties: 0,
    isAdmin: false,
  },
  {
    id: "charlie",
    name: "Charlie",
    email: "charlie@example.com",
    joinDate: "2024-03-10",
    isFlagged: true,
    penalties: 2,
    flagReason: "Spam reviews",
    isAdmin: false,
  },
];

interface UserWatchlist {
  [userId: string]: number[];
}

interface Review {
  id: number;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

const mapApiUserToUser = (apiUser: ApiUser): User => ({
  id: apiUser.id,
  name: apiUser.username,
  email: apiUser.email,
  joinDate: new Date().toISOString().split("T")[0],
  isFlagged: false,
  penalties: apiUser.penalties?.length ?? 0,
  flagReason: undefined,
  isAdmin: apiUser.role === "admin",
  watchlistCount: apiUser.watchlist?.length ?? 0,
  reviewCount: apiUser.reviews?.length ?? 0,
});

export default function App() {
  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem("auth_token"));
  const [authUser, setAuthUser] = useState<ApiUser | null>(null);
  const [authView, setAuthView] = useState<"login" | "register">("login");
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState("");
  const [activeSection, setActiveSection] = useState("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [sortBy, setSortBy] = useState<"title" | "rating" | "year">("title");
  const [filterGenre, setFilterGenre] = useState<string>("all");
  const [movies, setMovies] = useState<Movie[]>(initialMovies);
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [watchlists, setWatchlists] = useState<UserWatchlist>({
    alice: [1, 4],
    bob: [2, 3],
    charlie: [1, 2, 5],
  });
  const [reviews, setReviews] = useState<Review[]>([
    {
      id: 1,
      userId: "alice",
      userName: "Alice",
      rating: 9,
      comment:
        "An absolutely stunning visual masterpiece! The space scenes were breathtaking.",
      date: "2024-10-20",
    },
    {
      id: 4,
      userId: "bob",
      userName: "Bob",
      rating: 10,
      comment:
        "A must-watch for anyone who loves cinema. Beautifully crafted story.",
      date: "2024-10-18",
    },
  ]);
  const [isRestoringSession, setIsRestoringSession] = useState(true);

  const syncUserFromApi = (apiUser: ApiUser) => {
    setUsers((prev) => {
      const existing = prev.find((u) => u.id === apiUser.id);
      if (existing) {
        return prev.map((u) =>
          u.id === apiUser.id
            ? {
                ...existing,
                name: apiUser.username,
                email: apiUser.email,
                isAdmin: apiUser.role === "admin",
                penalties: apiUser.penalties?.length ?? existing.penalties,
                watchlistCount: apiUser.watchlist?.length ?? existing.watchlistCount,
                reviewCount: apiUser.reviews?.length ?? existing.reviewCount,
              }
            : u,
        );
      }
      return [...prev, mapApiUserToUser(apiUser)];
    });

    setWatchlists((prev) => {
      if (prev[apiUser.id]) {
        return prev;
      }
      const numericList =
        apiUser.watchlist?.map((id) => Number(id)).filter((id) => Number.isFinite(id)) ?? [];
      return { ...prev, [apiUser.id]: numericList };
    });
  };

  const handleAuthSuccess = (response: AuthResponse) => {
    syncUserFromApi(response.user);
    setAuthToken(response.token);
    setAuthUser(response.user);
    setCurrentUser(response.user.username);
    setAuthError(null);
    setActiveSection("home");
  };

  const handleRegisterSubmit = async (data: { name: string; email: string; password: string; isAdmin: boolean }) => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const response = await registerRequest({
        username: data.name,
        email: data.email,
        password: data.password,
        role: data.isAdmin ? "admin" : "user",
      });
      handleAuthSuccess(response);
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Registration failed");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLoginSubmit = async (credentials: { email: string; password: string }) => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const response = await loginRequest(credentials);
      handleAuthSuccess(response);
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Login failed");
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    if (authToken) {
      localStorage.setItem("auth_token", authToken);
    } else {
      localStorage.removeItem("auth_token");
    }
  }, [authToken]);

  useEffect(() => {
    if (!authToken) {
      setAuthUser(null);
      setIsRestoringSession(false);
      return;
    }

    let cancelled = false;
    setIsRestoringSession(true);

    fetchCurrentUser(authToken)
      .then((user) => {
        if (cancelled) return;
        syncUserFromApi(user);
        setAuthUser(user);
        setCurrentUser(user.username);
        setAuthError(null);
      })
      .catch(() => {
        if (cancelled) return;
        setAuthToken(null);
        setAuthUser(null);
        setAuthError("Session expired. Please sign in again.");
      })
      .finally(() => {
        if (!cancelled) {
          setIsRestoringSession(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [authToken]);

  const isAuthenticated = Boolean(authToken && authUser);

  const currentUserObj = users.find((u) => u.name === currentUser);
  const authUserFromList = authUser ? users.find((u) => u.id === authUser.id) : undefined;
  const effectiveUser = currentUserObj ?? authUserFromList ?? users[0];
  const currentUserId = effectiveUser?.id || authUser?.id || "";
  const currentUserName = effectiveUser?.name || authUser?.username || "";
  const currentUserEmail = effectiveUser?.email || authUser?.email;
  const isAdmin = effectiveUser?.isAdmin || (authUser?.role === "admin");

  const handleWatchlistToggle = (movieId: number) => {
    if (!currentUserId) {
      return;
    }
    setWatchlists((prev) => {
      const userList = prev[currentUserId] || [];
      const isInList = userList.includes(movieId);

      return {
        ...prev,
        [currentUserId]: isInList
          ? userList.filter((id) => id !== movieId)
          : [...userList, movieId],
      };
    });
  };

  const handleAddReview = (movieId: number, rating: number, comment: string) => {
    if (!currentUserId) {
      return;
    }
    const newReview: Review = {
      id: movieId,
      userId: currentUserId,
      userName: currentUserName || currentUser,
      rating,
      comment,
      date: new Date().toISOString().split("T")[0],
    };
    setReviews((prev) => [...prev, newReview]);
  };

  const handleMovieClick = (movie: Movie) => {
    setSelectedMovie(movie);
    setIsDialogOpen(true);
  };

  const handleDeleteMovie = (movieId: number) => {
    setMovies((prev) => prev.filter((m) => m.id !== movieId));
    setReviews((prev) => prev.filter((r) => r.id !== movieId));
    setWatchlists((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((user) => {
        updated[user] = updated[user].filter((id) => id !== movieId);
      });
      return updated;
    });
  };

  const handleAddMovie = (newMovie: Omit<Movie, "id">) => {
    const maxId = Math.max(...movies.map((m) => m.id), 0);
    const movieWithId: Movie = {
      ...newMovie,
      id: maxId + 1,
    };
    setMovies((prev) => [...prev, movieWithId]);
  };

  const handleDeleteReview = (movieId: number, userId: string, date: string) => {
    setReviews((prev) =>
      prev.filter(
        (r) => !(r.id === movieId && r.userId === userId && r.date === date),
      ),
    );
  };

  const handleDeleteUser = (userId: string) => {
    setUsers((prev) => {
      const filtered = prev.filter((u) => u.id !== userId);
      if (currentUserId === userId && filtered.length > 0) {
        setCurrentUser(filtered[0].name);
      }
      return filtered;
    });
    setWatchlists((prev) => {
      const updated = { ...prev };
      delete updated[userId];
      return updated;
    });
    setReviews((prev) => prev.filter((r) => r.userId !== userId));

    if (authUser?.id === userId) {
      setAuthToken(null);
      setAuthUser(null);
      setCurrentUser("");
    }
  };

  const handleFlagUser = (userId: string, reason: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, isFlagged: true, flagReason: reason } : u,
      ),
    );
  };

  const handleUnflagUser = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, isFlagged: false, flagReason: undefined } : u,
      ),
    );
  };

  const handleAddPenalty = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, penalties: u.penalties + 1 } : u,
      ),
    );
  };

  const handleRemovePenalty = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId
          ? { ...u, penalties: Math.max(0, u.penalties - 1) }
          : u,
      ),
    );
  };

  const currentWatchlist = currentUserId ? watchlists[currentUserId] || [] : [];
  const allGenres = Array.from(new Set(movies.flatMap((movie) => movie.genre)));

  const filteredMovies = movies
    .filter((movie) => {
      const matchesSearch =
        searchQuery === "" ||
        movie.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        movie.genre.some((g) =>
          g.toLowerCase().includes(searchQuery.toLowerCase()),
        );

      const matchesGenre =
        filterGenre === "all" || movie.genre.includes(filterGenre);

      if (activeSection === "watchlist") {
        return (
          matchesSearch && matchesGenre && currentWatchlist.includes(movie.id)
        );
      }

      return matchesSearch && matchesGenre;
    })
    .sort((a, b) => {
      if (sortBy === "title") {
        return a.title.localeCompare(b.title);
      } else if (sortBy === "rating") {
        return b.rating - a.rating;
      } else if (sortBy === "year") {
        return b.year - a.year;
      }
      return 0;
    });

  const userManagementData = useMemo(
    () =>
      users.map((user) => ({
        ...user,
        watchlistCount: watchlists[user.id]?.length ?? 0,
        reviewCount: reviews.filter((review) => review.userId === user.id).length,
      })),
    [users, watchlists, reviews],
  );

  const displayTitle =
    activeSection === "home"
      ? "Latest Movies"
      : activeSection === "watchlist"
        ? "My Watchlist"
        : activeSection.toUpperCase();

  if (isRestoringSession) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center">
        Restoring your session...
      </div>
    );
  }

  if (!isAuthenticated) {
    if (authView === "register") {
      return (
        <RegisterScreen
          onRegister={handleRegisterSubmit}
          onSwitchToLogin={() => {
            setAuthView("login");
            setAuthError(null);
          }}
          errorMessage={authError}
          isSubmitting={authLoading}
        />
      );
    }

    return (
      <LoginScreen
        onLogin={handleLoginSubmit}
        onSwitchToRegister={() => {
          setAuthView("register");
          setAuthError(null);
        }}
        errorMessage={authError}
        isSubmitting={authLoading}
      />
    );
  }

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        onAccessAdmin={() => isAdmin}
      />

      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {activeSection === "admin" ? (
            <AdminPanel
              movies={movies}
              users={users}
              reviews={reviews}
              watchlists={watchlists}
              onDeleteMovie={handleDeleteMovie}
              onAddMovie={handleAddMovie}
              onDeleteReview={handleDeleteReview}
              onDeleteUser={handleDeleteUser}
              onFlagUser={handleFlagUser}
              onUnflagUser={handleUnflagUser}
              onAddPenalty={handleAddPenalty}
              onRemovePenalty={handleRemovePenalty}
            />
          ) : activeSection === "docs" ? (
            <ApiDocs />
          ) : activeSection === "admin-users" ? (
            <UserManagement
              users={userManagementData}
              currentUser={currentUserId}
              onUserChange={(userId) => {
                const selected = users.find((u) => u.id === userId);
                if (selected) setCurrentUser(selected.name);
              }}
            />
          ) : (
            <>
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <div className="relative flex-1 max-w-2xl">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                    <Input
                      type="text"
                      placeholder="Quick search..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 bg-neutral-900 border-neutral-800 text-white placeholder:text-neutral-500"
                    />
                  </div>
                  <div className="ml-4">
                    <UserSwitcher
                      currentUser={currentUserName || ""}
                      currentUserEmail={currentUserEmail}
                      onSignOut={() => {
                        setAuthToken(null);
                        setAuthUser(null);
                        setCurrentUser("");
                        setActiveSection("home");
                        setAuthView("login");
                      }}
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="outline"
                        className="bg-neutral-900 border-neutral-800 gap-2"
                      >
                        <ArrowUpDown className="h-4 w-4" />
                        Sort: {sortBy === "title" ? "Title" : sortBy === "rating" ? "Rating" : "Year"}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-neutral-900 border-neutral-800">
                      <DropdownMenuItem onClick={() => setSortBy("title")}>
                        Title
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setSortBy("rating")}>
                        Rating
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setSortBy("year")}>
                        Year
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="outline"
                        className="bg-neutral-900 border-neutral-800 gap-2"
                      >
                        <SlidersHorizontal className="h-4 w-4" />
                        Filter: {filterGenre === "all" ? "All Genres" : filterGenre}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-neutral-900 border-neutral-800">
                      <DropdownMenuItem onClick={() => setFilterGenre("all")}>
                        All Genres
                      </DropdownMenuItem>
                      {allGenres.map((genre) => (
                        <DropdownMenuItem key={genre} onClick={() => setFilterGenre(genre)}>
                          {genre}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              {activeSection === "home" && (
                <>
                  <div className="mb-8">
                    <MovieCarousel slides={carouselSlides} />
                  </div>

                  <div className="mb-8">
                    <div className="mb-4">
                      <h2 className="text-2xl mb-1">Trending Now</h2>
                      <p className="text-neutral-400">Popular movies this week</p>
                    </div>
                    <div className="px-12">
                      <Carousel
                        opts={{
                          align: "start",
                          loop: true,
                        }}
                        className="w-full"
                      >
                        <CarouselContent className="-ml-4">
                          {movies.slice(0, 12).map((movie) => (
                            <CarouselItem key={movie.id} className="pl-4 basis-1/2 md:basis-1/3 lg:basis-1/4 xl:basis-1/6">
                              <MovieCard
                                movie={movie}
                                isInWatchlist={currentWatchlist.includes(movie.id)}
                                onWatchlistToggle={handleWatchlistToggle}
                                onMovieClick={handleMovieClick}
                              />
                            </CarouselItem>
                          ))}
                        </CarouselContent>
                        <CarouselPrevious className="bg-neutral-800 border-neutral-700 hover:bg-neutral-700 text-white" />
                        <CarouselNext className="bg-neutral-800 border-neutral-700 hover:bg-neutral-700 text-white" />
                      </Carousel>
                    </div>
                  </div>

                  {isAdmin ? (
                    <AdminDashboard
                      users={users}
                      movies={movies}
                      reviews={reviews}
                      watchlists={watchlists}
                    />
                  ) : effectiveUser ? (
                    <UserDashboard
                      currentUser={effectiveUser}
                      movies={movies}
                      watchlist={currentWatchlist}
                      reviews={reviews}
                    />
                  ) : null}
                </>
              )}

              {(activeSection === "watchlist" ||
                searchQuery !== "" ||
                filterGenre !== "all") && (
                <>
                  <div className="mb-6">
                    <h2 className="text-2xl mb-1">{displayTitle}</h2>
                    <p className="text-neutral-400">
                      {filteredMovies.length} {filteredMovies.length === 1 ? "movie" : "movies"}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {filteredMovies.map((movie) => (
                      <MovieCard
                        key={movie.id}
                        movie={movie}
                        isInWatchlist={currentWatchlist.includes(movie.id)}
                        onWatchlistToggle={handleWatchlistToggle}
                        onMovieClick={handleMovieClick}
                      />
                    ))}
                  </div>

                  {filteredMovies.length === 0 && (
                    <div className="text-center py-16 text-neutral-500">
                      <p>No movies found.</p>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>

      <MovieDialog
        movie={selectedMovie}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        isInWatchlist={
          selectedMovie ? currentWatchlist.includes(selectedMovie.id) : false
        }
        onWatchlistToggle={handleWatchlistToggle}
        reviews={reviews}
        onAddReview={handleAddReview}
      />
    </div>
  );
}
