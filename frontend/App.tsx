import { useState } from "react";
import { Search, SlidersHorizontal, ArrowUpDown } from "lucide-react";
import { Input } from "./components/ui/input";
import { Sidebar } from "./components/Sidebar";
import { MovieCard, Movie } from "./components/MovieCard";
import { MovieCarousel } from "./components/MovieCarousel";
import { MovieDialog } from "./components/MovieDialog";
import { AdminPanel } from "./components/AdminPanel";
import { ApiDocs } from "./components/ApiDocs";
import { UserManagement } from "./components/UserManagement";
import { UserSwitcher } from "./components/UserSwitcher";
import { UserDashboard } from "./components/UserDashboard";
import { AdminDashboard } from "./components/AdminDashboard";
import { RegisterScreen } from "./components/RegisterScreen";
import { Button } from "./components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./components/ui/dropdown-menu";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./components/ui/carousel";

// Mock movie data
const initialMovies: Movie[] = [
  {
    id: 1,
    title: "The Cosmic Journey",
    year: 2024,
    rating: 8.5,
    poster: "https://images.unsplash.com/photo-1687985826611-80b714011d0b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2klMjBmaSUyMHNwYWNlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Sci-Fi", "Adventure"],
    description: "An epic journey through the cosmos exploring the mysteries of the universe and humanity's place within it.",
    ageRating: "PG-13",
  },
  {
    id: 2,
    title: "Urban Legends",
    year: 2023,
    rating: 7.8,
    poster: "https://images.unsplash.com/photo-1755076347925-fe1e04401c90?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhY3Rpb24lMjBtb3ZpZSUyMHNjZW5lfGVufDF8fHx8MTc2MTI5NzE1M3ww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Action", "Thriller"],
    description: "A gripping tale of mystery and suspense set in the heart of the city.",
    ageRating: "R",
  },
  {
    id: 3,
    title: "Love in Paris",
    year: 2024,
    rating: 7.2,
    poster: "https://images.unsplash.com/photo-1627964464837-6328f5931576?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb21hbnRpYyUyMG1vdmllJTIwY291cGxlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Romance", "Drama"],
    description: "A heartwarming story of love and connection in the city of lights.",
    ageRating: "PG-13",
  },
  {
    id: 4,
    title: "Cinema Dreams",
    year: 2023,
    rating: 8.9,
    poster: "https://images.unsplash.com/photo-1655367574486-f63675dd69eb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb3ZpZSUyMGNpbmVtYSUyMHBvc3RlcnxlbnwxfHx8fDE3NjEzMzI3NTV8MA&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Drama", "Biography"],
    description: "The inspiring true story of filmmakers who changed cinema forever.",
    ageRating: "PG",
  },
  {
    id: 5,
    title: "Dark Horizons",
    year: 2024,
    rating: 8.1,
    poster: "https://images.unsplash.com/photo-1687985826611-80b714011d0b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2klMjBmaSUyMHNwYWNlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Sci-Fi", "Horror"],
    description: "When space exploration goes wrong, a crew must fight for survival.",
    ageRating: "R",
  },
  {
    id: 6,
    title: "The Last Stand",
    year: 2023,
    rating: 7.5,
    poster: "https://images.unsplash.com/photo-1755076347925-fe1e04401c90?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhY3Rpb24lMjBtb3ZpZSUyMHNjZW5lfGVufDF8fHx8MTc2MTI5NzE1M3ww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Action", "Western"],
    description: "A lone hero must defend a small town against overwhelming odds.",
    ageRating: "PG-13",
  },
  {
    id: 7,
    title: "Summer's End",
    year: 2024,
    rating: 6.9,
    poster: "https://images.unsplash.com/photo-1627964464837-6328f5931576?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb21hbnRpYyUyMG1vdmllJTIwY291cGxlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Romance", "Coming of Age"],
    description: "A beautiful story about growing up and first love.",
    ageRating: "PG",
  },
  {
    id: 8,
    title: "Reel Magic",
    year: 2023,
    rating: 7.7,
    poster: "https://images.unsplash.com/photo-1655367574486-f63675dd69eb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb3ZpZSUyMGNpbmVtYSUyMHBvc3RlcnxlbnwxfHx8fDE3NjEzMzI3NTV8MA&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Fantasy", "Family"],
    description: "Discover the magic hidden within the silver screen.",
    ageRating: "PG",
  },
];

const carouselSlides = [
  {
    id: 1,
    image: "https://images.unsplash.com/photo-1687985826611-80b714011d0b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2klMjBmaSUyMHNwYWNlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    title: "The Cosmic Journey",
  },
  {
    id: 2,
    image: "https://images.unsplash.com/photo-1755076347925-fe1e04401c90?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhY3Rpb24lMjBtb3ZpZSUyMHNjZW5lfGVufDF8fHx8MTc2MTI5NzE1M3ww&ixlib=rb-4.1.0&q=80&w=1080",
    title: "Urban Legends",
  },
  {
    id: 3,
    image: "https://images.unsplash.com/photo-1655367574486-f63675dd69eb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb3ZpZSUyMGNpbmVtYSUyMHBvc3RlcnxlbnwxfHx8fDE3NjEzMzI3NTV8MA&ixlib=rb-4.1.0&q=80&w=1080",
    title: "Cinema Dreams",
  },
];

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

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [showRegister, setShowRegister] = useState(false); // Set to false to show main app
  const [currentUser, setCurrentUser] = useState("Alice");
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
      comment: "An absolutely stunning visual masterpiece! The space scenes were breathtaking.",
      date: "2024-10-20",
    },
    {
      id: 4,
      userId: "bob",
      userName: "Bob",
      rating: 10,
      comment: "A must-watch for anyone who loves cinema. Beautifully crafted story.",
      date: "2024-10-18",
    },
  ]);

  const currentUserObj = users.find((u) => u.name === currentUser);
  const currentUserId = currentUserObj?.id || "alice";
  const isAdmin = currentUserObj?.isAdmin || false;

  const handleWatchlistToggle = (movieId: number) => {
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
    const newReview: Review = {
      id: movieId,
      userId: currentUserId,
      userName: currentUser,
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

  const handleEditMovie = (movie: Movie) => {
    setMovies((prev) => prev.map((m) => (m.id === movie.id ? movie : m)));
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
      prev.filter((r) => !(r.id === movieId && r.userId === userId && r.date === date))
    );
  };

  const handleDeleteUser = (userId: string) => {
    setUsers((prev) => prev.filter((u) => u.id !== userId));
    // Also clean up user's data
    setWatchlists((prev) => {
      const updated = { ...prev };
      delete updated[userId];
      return updated;
    });
    setReviews((prev) => prev.filter((r) => r.userId !== userId));
    
    // Switch to another user if deleting current user
    if (currentUserId === userId && users.length > 1) {
      const remainingUser = users.find((u) => u.id !== userId);
      if (remainingUser) {
        setCurrentUser(remainingUser.name);
      }
    }
  };

  const handleFlagUser = (userId: string, reason: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, isFlagged: true, flagReason: reason } : u
      )
    );
  };

  const handleUnflagUser = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, isFlagged: false, flagReason: undefined } : u
      )
    );
  };

  const handleAddPenalty = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, penalties: u.penalties + 1 } : u
      )
    );
  };

  const handleRemovePenalty = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, penalties: Math.max(0, u.penalties - 1) } : u
      )
    );
  };

  const currentWatchlist = watchlists[currentUserId] || [];

  // Get all unique genres
  const allGenres = Array.from(new Set(movies.flatMap((movie) => movie.genre)));

  const filteredMovies = movies
    .filter((movie) => {
      const matchesSearch =
        searchQuery === "" ||
        movie.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        movie.genre.some((g) => g.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesGenre =
        filterGenre === "all" || movie.genre.includes(filterGenre);

      if (activeSection === "watchlist") {
        return matchesSearch && matchesGenre && currentWatchlist.includes(movie.id);
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

  const displayTitle =
    activeSection === "home"
      ? "Latest Movies"
      : activeSection === "watchlist"
      ? "My Watchlist"
      : activeSection.toUpperCase();

  // Show register screen if not authenticated
  if (!isAuthenticated && showRegister) {
    return (
      <RegisterScreen
        onRegister={(data) => {
          // Demo: Add new user and authenticate
          const newUser = {
            id: data.name.toLowerCase(),
            name: data.name,
            email: data.email,
            joinDate: new Date().toISOString().split("T")[0],
            isFlagged: false,
            penalties: 0,
            isAdmin: data.isAdmin,
          };
          setUsers([...users, newUser]);
          setCurrentUser(data.name);
          setIsAuthenticated(true);
          setShowRegister(false);
        }}
        onSwitchToLogin={() => {
          // For demo, just authenticate as Alice
          setIsAuthenticated(true);
          setShowRegister(false);
        }}
      />
    );
  }

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
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
              onEditMovie={handleEditMovie}
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
                      currentUser={currentUser}
                      currentUserEmail={currentUserObj?.email}
                      onSignOut={() => {
                        // Sign out and show register screen
                        setIsAuthenticated(false);
                        setShowRegister(true);
                        setCurrentUser("Alice");
                        setActiveSection("home");
                      }}
                    />
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="bg-neutral-900 border-neutral-800 gap-2">
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
                      <Button variant="outline" className="bg-neutral-900 border-neutral-800 gap-2">
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
                  ) : currentUserObj ? (
                    <UserDashboard
                      currentUser={currentUserObj}
                      movies={movies}
                      watchlist={currentWatchlist}
                      reviews={reviews}
                    />
                  ) : null}
                </>
              )}

              {(activeSection === "watchlist" || searchQuery !== "" || filterGenre !== "all") && (
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
        isInWatchlist={selectedMovie ? currentWatchlist.includes(selectedMovie.id) : false}
        onWatchlistToggle={handleWatchlistToggle}
        reviews={reviews}
        onAddReview={handleAddReview}
        currentUser={currentUser}
      />
    </div>
  );
}