import { useEffect, useState } from "react";
import { Search, SlidersHorizontal, ArrowUpDown } from "lucide-react";
import { Input } from "./components/ui/input";
import { Sidebar } from "./components/Sidebar";
import { MovieCard, Movie } from "./components/MovieCard";
import { MovieCarousel } from "./components/MovieCarousel";
import { MovieDialog } from "./components/MovieDialog";
import { AdminPanel } from "./components/AdminPanel";
import { ApiDocs } from "./components/ApiDocs";
import { UserSwitcher } from "./components/UserSwitcher";
import { UserDashboard } from "./components/UserDashboard";
import { AdminDashboard } from "./components/AdminDashboard";
import { RegisterScreen } from "./components/RegisterScreen";
import { LoginScreen } from "./components/LoginScreen";
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
    id: "the-cosmic-journey",
    title: "The Cosmic Journey",
    year: 2024,
    rating: 8.5,
    poster: "https://images.unsplash.com/photo-1687985826611-80b714011d0b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2klMjBmaSUyMHNwYWNlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Sci-Fi", "Adventure"],
    description: "An epic journey through the cosmos exploring the mysteries of the universe and humanity's place within it.",
    ageRating: "PG-13",
  },
  {
    id: "urban-legends",
    title: "Urban Legends",
    year: 2023,
    rating: 7.8,
    poster: "https://images.unsplash.com/photo-1755076347925-fe1e04401c90?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhY3Rpb24lMjBtb3ZpZSUyMHNjZW5lfGVufDF8fHx8MTc2MTI5NzE1M3ww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Action", "Thriller"],
    description: "A gripping tale of mystery and suspense set in the heart of the city.",
    ageRating: "R",
  },
  {
    id: "love-in-paris",
    title: "Love in Paris",
    year: 2024,
    rating: 7.2,
    poster: "https://images.unsplash.com/photo-1627964464837-6328f5931576?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb21hbnRpYyUyMG1vdmllJTIwY291cGxlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Romance", "Drama"],
    description: "A heartwarming story of love and connection in the city of lights.",
    ageRating: "PG-13",
  },
  {
    id: "cinema-dreams",
    title: "Cinema Dreams",
    year: 2023,
    rating: 8.9,
    poster: "https://images.unsplash.com/photo-1655367574486-f63675dd69eb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb3ZpZSUyMGNpbmVtYSUyMHBvc3RlcnxlbnwxfHx8fDE3NjEzMzI3NTV8MA&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Drama", "Biography"],
    description: "The inspiring true story of filmmakers who changed cinema forever.",
    ageRating: "PG",
  },
  {
    id: "dark-horizons",
    title: "Dark Horizons",
    year: 2024,
    rating: 8.1,
    poster: "https://images.unsplash.com/photo-1687985826611-80b714011d0b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2klMjBmaSUyMHNwYWNlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Sci-Fi", "Horror"],
    description: "When space exploration goes wrong, a crew must fight for survival.",
    ageRating: "R",
  },
  {
    id: "the-last-stand",
    title: "The Last Stand",
    year: 2023,
    rating: 7.5,
    poster: "https://images.unsplash.com/photo-1755076347925-fe1e04401c90?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhY3Rpb24lMjBtb3ZpZSUyMHNjZW5lfGVufDF8fHx8MTc2MTI5NzE1M3ww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Action", "Western"],
    description: "A lone hero must defend a small town against overwhelming odds.",
    ageRating: "PG-13",
  },
  {
    id: "summers-end",
    title: "Summer's End",
    year: 2024,
    rating: 6.9,
    poster: "https://images.unsplash.com/photo-1627964464837-6328f5931576?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb21hbnRpYyUyMG1vdmllJTIwY291cGxlfGVufDF8fHx8MTc2MTM0NjMwNnww&ixlib=rb-4.1.0&q=80&w=1080",
    genre: ["Romance", "Coming of Age"],
    description: "A beautiful story about growing up and first love.",
    ageRating: "PG",
  },
  {
    id: "reel-magic",
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

const AUTH_STORAGE_KEY = "imdbest.auth";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const slugify = (value: string) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "") || "movie";

const buildPosterUrl = (title: string) =>
  `https://source.unsplash.com/featured/600x900/?movie,${encodeURIComponent(title || "film")}`;

const normalizeYear = (value?: string) => {
  if (!value) return new Date().getFullYear();
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) {
    const numericYear = Number(value.slice(0, 4));
    return Number.isNaN(numericYear) ? new Date().getFullYear() : numericYear;
  }
  return new Date(timestamp).getFullYear();
};

const mapBackendMovie = (summary: any, metadata: Record<string, any>): Movie => {
  const title = metadata?.title || summary?.title || "Untitled";
  const genre = Array.isArray(metadata?.movieGenres) && metadata.movieGenres.length > 0
    ? metadata.movieGenres
    : ["Uncategorized"];

  return {
    id: summary?.id || slugify(title),
    title,
    year: normalizeYear(metadata?.datePublished || summary?.releaseDate),
    rating: Number(summary?.userRatingAverage ?? summary?.imdbRating ?? metadata?.movieIMDbRating ?? 0) || 0,
    poster: metadata?.poster || buildPosterUrl(title),
    genre,
    description: metadata?.description || "Description not available.",
    ageRating: metadata?.ageRating || "NR",
  };
};

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

interface AuthUser {
  id: string;
  username: string;
  email: string;
  registered_at?: string | null;
  reviews?: string[];
  watchlist?: string[];
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
  [userId: string]: string[];
}

interface Review {
  id: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [currentUser, setCurrentUser] = useState("");
  const [activeSection, setActiveSection] = useState("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [sortBy, setSortBy] = useState<"title" | "rating" | "year">("title");
  const [filterGenre, setFilterGenre] = useState<string>("all");
  const [movies, setMovies] = useState<Movie[]>(initialMovies);
  const [isLoadingMovies, setIsLoadingMovies] = useState(false);
  const [movieError, setMovieError] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [watchlists, setWatchlists] = useState<UserWatchlist>({
    alice: ["the-cosmic-journey", "cinema-dreams"],
    bob: ["urban-legends", "love-in-paris"],
    charlie: ["the-cosmic-journey", "urban-legends", "dark-horizons"],
  });
  const [reviews, setReviews] = useState<Review[]>([
    {
      id: "the-cosmic-journey",
      userId: "alice",
      userName: "Alice",
      rating: 9,
      comment: "An absolutely stunning visual masterpiece! The space scenes were breathtaking.",
      date: "2024-10-20",
    },
    {
      id: "cinema-dreams",
      userId: "bob",
      userName: "Bob",
      rating: 10,
      comment: "A must-watch for anyone who loves cinema. Beautifully crafted story.",
      date: "2024-10-18",
    },
  ]);

  const decodeTokenRole = (token: string | null) => {
    if (!token) return "user";
    try {
      const payload = token.split(".")[1];
      const padded = payload.padEnd(payload.length + ((4 - (payload.length % 4)) % 4), "=");
      const decoded = JSON.parse(atob(padded.replace(/-/g, "+").replace(/_/g, "/")));
      return decoded?.role || "user";
    } catch {
      return "user";
    }
  };

  const normalizeJoinDate = (value?: string | null) => {
    if (!value) {
      return new Date().toISOString().split("T")[0];
    }
    return value.split("T")[0];
  };

  const ensureUserRecord = (user: AuthUser, tokenRole: string) => {
    const normalized: User = {
      id: user.id,
      name: user.username,
      email: user.email,
      joinDate: normalizeJoinDate(user.registered_at),
      isFlagged: false,
      penalties: 0,
      isAdmin: tokenRole === "admin",
    };

    setUsers((prev) => {
      const existingIndex = prev.findIndex((u) => u.id === user.id || u.name === user.username);
      if (existingIndex === -1) {
        return [...prev, normalized];
      }
      const next = [...prev];
      next[existingIndex] = { ...next[existingIndex], ...normalized };
      return next;
    });

    setWatchlists((prev) => {
      if (prev[user.id]) {
        return prev;
      }
      return { ...prev, [user.id]: [] };
    });
  };

  const applySession = (token: string, user: AuthUser) => {
    const role = decodeTokenRole(token);
    setAuthToken(token);
    setAuthUser(user);
    setIsAuthenticated(true);
    setCurrentUser(user.username);
    ensureUserRecord(user, role);
  };

  const persistSession = (token: string, user: AuthUser) => {
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ token, user }));
    } catch {
      // ignore storage failures
    }
  };

  const clearSession = () => {
    try {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    } catch {
      // ignore storage failures
    }
  };

  const handleAuthSuccess = (token: string, user: AuthUser) => {
    applySession(token, user);
    persistSession(token, user);
    setAuthMode("login");
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAuthToken(null);
    setAuthUser(null);
    setCurrentUser("");
    setAuthMode("login");
    setAuthError(null);
    setActiveSection("home");
    clearSession();
  };

  const authorizedFetch = (input: RequestInfo | URL, init: RequestInit = {}) => {
    const headers = new Headers(init.headers || {});
    if (authToken) {
      headers.set("Authorization", `Bearer ${authToken}`);
    }
    return fetch(input, { ...init, headers });
  };

  const handleRegister = async (payload: { username: string; email: string; password: string }) => {
    setAuthError(null);
    setIsAuthLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/users/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data?.detail || "Registration failed. Please try again.");
      }
      handleAuthSuccess(data.token, data.user);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Registration failed. Please try again.";
      setAuthError(message);
    } finally {
      setIsAuthLoading(false);
    }
  };

  const handleLogin = async (payload: { username: string; password: string }) => {
    setAuthError(null);
    setIsAuthLoading(true);
    try {
      const params = new URLSearchParams({
        username: payload.username,
        password: payload.password,
      });
      const res = await fetch(`${API_BASE_URL}/users/login?${params.toString()}`, {
        method: "POST",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data?.detail || "Login failed. Please check your credentials.");
      }
      handleAuthSuccess(data.token, data.user);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Login failed. Please try again.";
      setAuthError(message);
    } finally {
      setIsAuthLoading(false);
    }
  };

  useEffect(() => {
    try {
      const stored = localStorage.getItem(AUTH_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as { token?: string; user?: AuthUser };
        if (parsed?.token && parsed?.user) {
          applySession(parsed.token, parsed.user);
          return;
        }
      }
    } catch {
      // ignore parse errors
    }
    setIsAuthenticated(false);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const fetchMovies = async () => {
      setIsLoadingMovies(true);
      setMovieError(null);
      try {
        const response = await authorizedFetch(`${API_BASE_URL}/search?q=&limit=50`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Backend responded with ${response.status}`);
        }
        const payload = await response.json();
        const summaries = Array.isArray(payload?.items) ? payload.items : [];

        if (summaries.length === 0) {
          setMovies(initialMovies);
          return;
        }

        const metadata = await Promise.all(
          summaries.map(async (summary: any) => {
            try {
              const metaRes = await authorizedFetch(`${API_BASE_URL}/movies/${summary.id}/metadata`, {
                signal: controller.signal,
              });
              if (!metaRes.ok) {
                return {};
              }
              return await metaRes.json();
            } catch {
              return {};
            }
          })
        );

        const normalized = summaries.map((summary: any, index: number) =>
          mapBackendMovie(summary, metadata[index] || {})
        );
        setMovies(normalized);
      } catch (error) {
        if ((error as Error).name === "AbortError") return;
        console.error("Failed to fetch movies", error);
        setMovieError("Unable to load movies from the backend. Showing local data.");
        setMovies(initialMovies);
      } finally {
        setIsLoadingMovies(false);
      }
    };

    fetchMovies();

    return () => controller.abort();
  }, [authToken]);

  const matchedUser = users.find((u) => u.name === currentUser);
  const fallbackUser =
    !matchedUser && authUser
      ? {
          id: authUser.id,
          name: authUser.username,
          email: authUser.email,
          joinDate: normalizeJoinDate(authUser.registered_at),
          isFlagged: false,
          penalties: 0,
          isAdmin: decodeTokenRole(authToken) === "admin",
        }
      : undefined;
  const currentUserObj = matchedUser || fallbackUser;
  const currentUserId = currentUserObj?.id || "alice";
  const isAdmin = currentUserObj?.isAdmin || false;
  useEffect(() => {
    if (!isAdmin && activeSection === "admin") {
      setActiveSection("home");
    }
  }, [isAdmin, activeSection]);

  const handleWatchlistToggle = (movieId: string) => {
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

  const handleAddReview = (movieId: string, rating: number, comment: string) => {
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

  const handleDeleteMovie = (movieId: string) => {
    setMovies((prev) => prev.filter((m) => m.id !== movieId));
    setReviews((prev) => prev.filter((r) => r.id !== movieId));
    setWatchlists((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((user) => {
        updated[user] = (updated[user] || []).filter((id) => id !== movieId);
      });
      return updated;
    });
  };

  const handleEditMovie = (movie: Movie) => {
    setMovies((prev) => prev.map((m) => (m.id === movie.id ? movie : m)));
  };

  const handleAddMovie = (newMovie: Omit<Movie, "id">) => {
    const baseId = slugify(newMovie.title || "movie");
    let uniqueId = baseId;
    let counter = 1;
    while (movies.some((m) => m.id === uniqueId)) {
      uniqueId = `${baseId}-${counter++}`;
    }
    const movieWithId: Movie = {
      ...newMovie,
      id: uniqueId,
      poster: newMovie.poster || buildPosterUrl(newMovie.title),
    };
    setMovies((prev) => [...prev, movieWithId]);
  };

  const handleDeleteReview = (movieId: string, userId: string, date: string) => {
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

  if (!isAuthenticated) {
    if (authMode === "register") {
      return (
        <RegisterScreen
          onRegister={handleRegister}
          onSwitchToLogin={() => {
            setAuthMode("login");
            setAuthError(null);
          }}
          errorMessage={authError}
          isSubmitting={isAuthLoading}
        />
      );
    }

    return (
      <LoginScreen
        onLogin={handleLogin}
        onSwitchToRegister={() => {
          setAuthMode("register");
          setAuthError(null);
        }}
        errorMessage={authError}
        isSubmitting={isAuthLoading}
      />
    );
  }

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        isAdmin={isAdmin}
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
                      currentUserEmail={currentUserObj?.email || authUser?.email}
                      onSignOut={handleLogout}
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

              {movieError && (
                <div className="mb-6 rounded border border-yellow-800 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-200">
                  {movieError}
                </div>
              )}

              {isLoadingMovies && !movieError && (
                <div className="mb-6 text-sm text-neutral-400">Loading movies from backend...</div>
              )}

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
