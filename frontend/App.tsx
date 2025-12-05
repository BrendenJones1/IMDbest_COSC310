import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Search, Star } from "lucide-react";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Sidebar } from "./components/Sidebar";
import { MovieCard, Movie } from "./components/MovieCard";
import { MovieCarousel } from "./components/MovieCarousel";
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

const API_BASE_URL =
  (import.meta as unknown as { env: { VITE_API_BASE_URL?: string } }).env
    .VITE_API_BASE_URL ?? "http://localhost:8000";

const hashStringToPositiveInt = (value: string) => {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0; // Convert to 32bit integer
  }
  return Math.abs(hash) + 1;
};

const coerceNumericId = (
  value: string | number | undefined,
  fallbackSeed: string
): number => {
  if (typeof value === "number" && Number.isFinite(value)) {
    const normalized = Math.floor(Math.abs(value));
    return normalized > 0 ? normalized : hashStringToPositiveInt(fallbackSeed);
  }

  if (typeof value === "string" && value.trim().length > 0) {
    const numeric = Number(value);
    if (!Number.isNaN(numeric)) {
      const normalized = Math.floor(Math.abs(numeric));
      if (normalized > 0) {
        return normalized;
      }
    }
    return hashStringToPositiveInt(value);
  }

  return hashStringToPositiveInt(fallbackSeed || `${Math.random()}`);
};

const mapBackendUser = (backendUser: any): User => {
  const fallbackId =
    backendUser.id ??
    backendUser.backendId ??
    Math.random().toString(36).slice(2);
  const backendId = fallbackId;
  const username = backendUser.username || backendUser.email || `user-${backendId}`;
  const joinDate = backendUser.registered_at
    ? backendUser.registered_at.split("T")[0]
    : new Date().toISOString().split("T")[0];
  const numericId = coerceNumericId(backendUser.id ?? backendUser.backendId, username);

  return {
    id: username,
    name: username,
    email: backendUser.email || "",
    password: "",
    joinDate,
    isFlagged: Boolean(backendUser.isFlagged ?? backendUser.is_flagged ?? false),
    penalties: Array.isArray(backendUser.penalties)
      ? backendUser.penalties.length
      : Number(backendUser.penalties ?? 0),
    flagReason: backendUser.flagReason,
    isAdmin: backendUser.role === "admin",
    backendId,
    numericId,
  };
};

const backendSortKeyFromUI = (value: "title" | "rating" | "year") => {
  if (value === "rating") return "user_rating";
  if (value === "year") return "release_date";
  return "title";
};

const toNumber = (value: any, fallback = 0): number => {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
};

const parseCount = (value: any): number => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const trimmed = value.trim().toLowerCase().replace(/,/g, "");
    const match = trimmed.match(/^([\d.]+)\s*([km])?$/);
    if (match) {
      const num = parseFloat(match[1]);
      if (!Number.isFinite(num)) return 0;
      const suffix = match[2];
      if (suffix === "k") return Math.round(num * 1_000);
      if (suffix === "m") return Math.round(num * 1_000_000);
      return Math.round(num);
    }
    const num = Number(trimmed);
    return Number.isFinite(num) ? num : 0;
  }
  return 0;
};

const formatCompactNumber = (value: number | undefined | null) => {
  if (!value || !Number.isFinite(value) || value <= 0) return "N/A";
  return new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(
    value
  );
};

const parseDurationMinutes = (raw: any): number => {
  if (typeof raw === "number" && Number.isFinite(raw)) return raw;
  if (typeof raw === "string") {
    const trimmed = raw.trim().toLowerCase();
    const hm = trimmed.match(/(?:(\d+)\s*h(?:ours?)?\s*)?(?:(\d+)\s*m(?:in)?(?:utes?)?)?/);
    if (hm && (hm[1] || hm[2])) {
      const h = Number(hm[1] || 0);
      const m = Number(hm[2] || 0);
      if (Number.isFinite(h) && Number.isFinite(m)) return h * 60 + m;
    }
    const numeric = Number(trimmed);
    if (Number.isFinite(numeric)) return numeric;
  }
  return 0;
};

const TRAILER_FALLBACKS: Record<string, string> = {
  "forrest gump": "XHhAG-YLdk8",
  "the avengers": "eOrNdBpGMv8",
  "avengers endgame": "TcMBFSGVi1c",
  "spiderman no way home": "JfVOs4VSpmA",
  "the dark knight": "EXeTwQWrcwY",
  "joker": "t433PEQGErc",
  "pulp fiction": "s7EdQ4FqbhY",
  "thor ragnarok": "ue80QwXMRHg",
  "morbius": "oZ6iiRrz1SY",
  "john wick chapter 3  parabellum": "M7XM597XO94",
  "return to silent hill": "5gcn9bWiwyo",
};

const formatDuration = (raw: any) => {
  const minutes = parseDurationMinutes(raw);
  if (!minutes || minutes <= 0) return "N/A";
  const hrs = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (!hrs) return `${mins}m`;
  return `${hrs}h${mins ? ` ${mins}m` : ""}`;
};

const computeTrailerUrl = (meta: Record<string, any> | null, title: string) => {
  const explicit =
    meta?.trailerUrl ||
    meta?.trailer ||
    meta?.videoUrl ||
    meta?.trailerURL ||
    meta?.trailer_url ||
    "";
  if (explicit) return explicit;

  const key = title.trim().toLowerCase();
  if (TRAILER_FALLBACKS[key]) {
    return `https://www.youtube.com/embed/${TRAILER_FALLBACKS[key]}`;
  }

  const query = encodeURIComponent(`${title} trailer`);
  return `https://www.youtube.com/embed?listType=search&list=${query}`;
};

const decodeRoleFromToken = (token: string | null) => {
  if (!token) return null;
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
    const decoded = JSON.parse(atob(padded));
    return decoded?.role ?? null;
  } catch {
    return null;
  }
};

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

const TRAILER_BY_ID: Record<string, string> = {
  "avengers-endgame":"TcMBFSGVi1c",
  "forrest-gump":"XHhAG-YLdk8",
  "john-wick-chapter-3-parabellum":"M7XM597XO94",
  "joker":"zAGVQLHvwOY",
  "morbius":"oZ6iiRrz1SY",
  "pulp-fiction":"s7EdQ4FqbhY",
  "spiderman-no-way-home":"JfVOs4VSpmA",
  "the-avengers":"eOrNdBpGMv8",
  "the-dark-knight":"EXeTwQWrcwY",
  "thor-ragnarok":"ue80QwXMRHg",
};

const setMovieTrailer = (movie: Movie): Movie => {
  const hardcodedTrailer = TRAILER_BY_ID[movie.id];

  return {
    ...movie,
    // prefer backend/metadata trailer if it exists, otherwise use hardcoded one
    trailerYoutubeId: movie.trailerYoutubeId ?? hardcodedTrailer,
  };
};

const mapBackendMovie = (summary: any, metadata: Record<string, any>): Movie => {
  const title = metadata?.title || summary?.title || "Untitled";
  const genre = Array.isArray(metadata?.movieGenres) && metadata.movieGenres.length > 0
      ? metadata.movieGenres
      : ["Uncategorized"];

  const durationMinutes = parseDurationMinutes(
    metadata?.duration ||
      metadata?.runtime ||
      metadata?.movieDuration ||
      metadata?.movieRuntime
  );

  const userReviews = parseCount(
    metadata?.totalUserReviews ??
      metadata?.userRatingCount ??
      metadata?.totalRatingCount
  );

  const rating = toNumber(
    metadata?.movieIMDbRating ??
      metadata?.userRatingAverage ??
      summary?.userRatingAverage ??
      summary?.imdbRating,
    0
  );

  const base: Movie = {
    id: summary?.id || slugify(title),
    title,
    year: normalizeYear(metadata?.datePublished || summary?.releaseDate),
    rating,
    poster: metadata?.poster || buildPosterUrl(title),
    genre,
    description: metadata?.description || "Description not available.",
    ageRating: metadata?.ageRating || "NR",
    durationMinutes: durationMinutes || undefined,
    userReviews: userReviews || undefined,
    ratingCount: parseCount(metadata?.totalRatingCount ?? metadata?.userRatingCount),
    imdbRating: toNumber(metadata?.movieIMDbRating ?? summary?.imdbRating, 0),
    trailerYoutubeId: metadata?.trailerYoutubeId || summary?.trailerYoutubeId,
  };

  return setMovieTrailer(base);
};

interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  joinDate: string;
  isFlagged: boolean;
  penalties: number;
  flagReason?: string;
  isAdmin: boolean;
  backendId?: string | number;
  numericId: number;
}

const mockUsers: User[] = [
  {
    id: "alice",
    name: "Alice",
    email: "alice@example.com",
    password: "password123",
    joinDate: "2024-01-15",
    isFlagged: false,
    penalties: 0,
    isAdmin: true,
    numericId: hashStringToPositiveInt("alice"),
  },
  {
    id: "bob",
    name: "Bob",
    email: "bob@example.com",
    password: "password123",
    joinDate: "2024-02-20",
    isFlagged: false,
    penalties: 0,
    isAdmin: false,
    numericId: hashStringToPositiveInt("bob"),
  },
  {
    id: "charlie",
    name: "Charlie",
    email: "charlie@example.com",
    password: "password123",
    joinDate: "2024-03-10",
    isFlagged: true,
    penalties: 2,
    flagReason: "Spam reviews",
    isAdmin: false,
    numericId: hashStringToPositiveInt("charlie"),
  },
  {
    id: "demo-admin",
    name: "admin@demo.com",
    email: "admin@demo.com",
    password: "password",
    joinDate: "2024-04-01",
    isFlagged: false,
    penalties: 0,
    isAdmin: true,
    numericId: hashStringToPositiveInt("demo-admin"),
  },
  {
    id: "demo-user",
    name: "user@demo.com",
    email: "user@demo.com",
    password: "password",
    joinDate: "2024-04-01",
    isFlagged: false,
    penalties: 0,
    isAdmin: false,
    numericId: hashStringToPositiveInt("demo-user"),
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

interface FlagReviewPayload {
  movieId: string;
  reviewUserId?: string;
  reviewUserName?: string;
  reason: string;
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authError, setAuthError] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState("Alice");
  const [activeSection, setActiveSection] = useState("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchSuggestions, setSearchSuggestions] = useState<Movie[]>([]);
  const [isSuggestionsOpen, setIsSuggestionsOpen] = useState(false);
  const [isSuggestionsLoading, setIsSuggestionsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [searchResultsTotal, setSearchResultsTotal] = useState(0);
  const [searchSortBy, setSearchSortBy] = useState<"title" | "rating" | "year">("title");
  const [searchSortOrder, setSearchSortOrder] = useState<"asc" | "desc">("asc");
  const [searchError, setSearchError] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [selectedMovieMeta, setSelectedMovieMeta] = useState<Record<string, any> | null>(null);
  const [sortBy, setSortBy] = useState<"title" | "rating" | "year">("title");
  const [filterGenre, setFilterGenre] = useState<string>("all");
  const [detailReviewInput, setDetailReviewInput] = useState({ rating: 5, comment: "" });
  const [movies, setMovies] = useState<Movie[]>(initialMovies);
  const [isLoadingMovies, setIsLoadingMovies] = useState(false);
  const [movieError, setMovieError] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>(mockUsers);
  const usersRef = useRef<User[]>(mockUsers);
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

  useEffect(() => {
    const controller = new AbortController();

    const fetchMovies = async () => {
      setIsLoadingMovies(true);
      setMovieError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/search?q=&limit=50`, {
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
              const metaRes = await fetch(`${API_BASE_URL}/movies/${summary.id}/metadata`, {
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
  }, []);

  useEffect(() => {
    usersRef.current = users;
  }, [users]);

  useEffect(() => {
    if (selectedMovie) {
      setDetailReviewInput({ rating: 5, comment: "" });
    }
  }, [selectedMovie?.id]);

  useEffect(() => {
    const controller = new AbortController();

    const fetchUsers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch users: ${response.status}`);
        }
        const payload = await response.json();
        const mapped = Array.isArray(payload) ? payload.map(mapBackendUser) : [];
        if (mapped.length > 0) {
          setUsers(mapped);
        }
      } catch (error) {
        console.warn("Using local users fallback. Unable to load backend users.", error);
      }
    };

    fetchUsers();

    return () => controller.abort();
  }, []);

  const currentUserObj = users.find((u) => u.name === currentUser);
  const currentUserId = currentUserObj?.id || "alice";
  const isAdmin = currentUserObj?.isAdmin || false;

  const fetchSearchResults = useCallback(
    async (
      term: string,
      options?: { sortBy?: "title" | "rating" | "year"; sortOrder?: "asc" | "desc"; limit?: number }
    ) => {
      const normalized = term.trim();
      if (!normalized) {
        setSearchResults([]);
        setSearchResultsTotal(0);
        setSearchError(null);
        return;
      }
      setIsSearching(true);
      setSearchError(null);
      const sortByValue = options?.sortBy ?? searchSortBy;
      const sortOrderValue = options?.sortOrder ?? searchSortOrder;
      setSearchSortBy(sortByValue);
      setSearchSortOrder(sortOrderValue);
      try {
        const params = new URLSearchParams();
        params.set("q", normalized);
        params.set("limit", String(options?.limit ?? 50));
        params.set("sort_by", backendSortKeyFromUI(sortByValue));
        params.set("sort_order", sortOrderValue);
        const res = await fetch(`${API_BASE_URL}/search?${params.toString()}`);
        if (!res.ok) {
          throw new Error(`Search failed (${res.status})`);
        }
        const payload = await res.json();
        const summaries = Array.isArray(payload?.items) ? payload.items : [];
        const metadata = await Promise.all(
          summaries.map(async (summary: any) => {
            try {
              const metaRes = await fetch(`${API_BASE_URL}/movies/${summary.id}/metadata`);
              if (!metaRes.ok) return {};
              return await metaRes.json();
            } catch {
              return {};
            }
          })
        );
        const combined = summaries.map((summary: any, idx: number) =>
          mapBackendMovie(summary, metadata[idx] || {})
        );
        setSearchResults(combined);
        setSearchResultsTotal(Number(payload?.total ?? combined.length));
        setActiveSection("search");
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Unable to search right now. Please try again.";
        setSearchError(message);
      } finally {
        setIsSearching(false);
      }
    },
    [API_BASE_URL, searchSortBy, searchSortOrder]
  );

  const fetchSearchSuggestions = useCallback(
    async (term: string, signal?: AbortSignal) => {
      const normalized = term.trim();
      if (!normalized) {
        setSearchSuggestions([]);
        return;
      }
      setIsSuggestionsLoading(true);
      try {
        const params = new URLSearchParams();
        params.set("q", normalized);
        params.set("limit", "6");
        params.set("sort_by", "title");
        const res = await fetch(`${API_BASE_URL}/search?${params.toString()}`, { signal });
        if (!res.ok) throw new Error("Failed to load suggestions");
        const payload = await res.json();
        const summaries = Array.isArray(payload?.items) ? payload.items : [];
        const metadata = await Promise.all(
          summaries.map(async (summary: any) => {
            try {
              const metaRes = await fetch(`${API_BASE_URL}/movies/${summary.id}/metadata`, {
                signal,
              });
              if (!metaRes.ok) return {};
              return await metaRes.json();
            } catch {
              return {};
            }
          })
        );
        const combined = summaries.map((summary: any, idx: number) =>
          mapBackendMovie(summary, metadata[idx] || {})
        );
        setSearchSuggestions(combined);
      } catch {
        setSearchSuggestions([]);
      } finally {
        setIsSuggestionsLoading(false);
      }
    },
    [API_BASE_URL]
  );

  useEffect(() => {
    const controller = new AbortController();
    if (!searchQuery.trim()) {
      setSearchSuggestions([]);
      setIsSuggestionsOpen(false);
      return;
    }
    setIsSuggestionsOpen(true);
    const t = setTimeout(() => {
      fetchSearchSuggestions(searchQuery, controller.signal);
    }, 250);
    return () => {
      controller.abort();
      clearTimeout(t);
    };
  }, [searchQuery, fetchSearchSuggestions]);

  useEffect(() => {
    if (activeSection !== "movie-detail" || !selectedMovie) {
      setSelectedMovieMeta(null);
      return;
    }
    const controller = new AbortController();
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/movies/${selectedMovie.id}/metadata`, {
          signal: controller.signal,
        });
        if (!res.ok) throw new Error("Failed to load movie details");
        const meta = await res.json();
        setSelectedMovieMeta(meta);
      } catch {
        setSelectedMovieMeta(null);
      }
    })();
    return () => controller.abort();
  }, [activeSection, selectedMovie?.id]);

  const handleSearchSubmit = async (term?: string) => {
    const query = (term ?? searchQuery).trim();
    if (!query) return;
    await fetchSearchResults(query);
    setIsSuggestionsOpen(false);
  };

  const resolveUsernameForLogin = async (identifier: string) => {
    const lowered = identifier.toLowerCase();
    const localMatch = usersRef.current.find(
      (u) =>
        u.email.toLowerCase() === lowered ||
        u.name.toLowerCase() === lowered
    );
    if (localMatch) {
      return localMatch.name;
    }

    if (!identifier.includes("@")) {
      return identifier;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/`);
      if (!response.ok) {
        return identifier;
      }
      const payload = await response.json();
      if (Array.isArray(payload)) {
        const fromBackend = payload.find(
          (user: any) =>
            typeof user.email === "string" &&
            user.email.toLowerCase() === lowered
        );
        if (fromBackend?.username) {
          return fromBackend.username;
        }
      }
    } catch {
      // ignore fetch errors and fall back to identifier
    }

    return identifier;
  };

  const handleWatchlistToggle = (movieId: string) => {
    if (!isAuthenticated) {
      setActiveSection("login");
      setAuthMode("login");
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

  const handleAddReview = (movieId: string, rating: number, comment: string) => {
    if (!isAuthenticated) {
      setActiveSection("login");
      setAuthMode("login");
      return;
    }
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

  const handleSubmitDetailReview = () => {
    if (!selectedMovie || !detailReviewInput.comment.trim()) return;
    handleAddReview(selectedMovie.id, detailReviewInput.rating, detailReviewInput.comment.trim());
    setDetailReviewInput({ rating: 5, comment: "" });
  };

  const handleFlagReview = async ({
    movieId,
    reviewUserId,
    reviewUserName,
    reason,
  }: FlagReviewPayload) => {
    if (!currentUserObj) {
      throw new Error("Please sign in to flag reviews.");
    }

    const trimmedReason = reason.trim();
    if (!trimmedReason) {
      throw new Error("Provide a short reason for the flag.");
    }

    const normalizedReviewerName = reviewUserName?.toLowerCase();
    const targetUser =
      users.find(
        (u) =>
          (reviewUserId && u.id === reviewUserId) ||
          (normalizedReviewerName && u.name.toLowerCase() === normalizedReviewerName)
      ) || null;

    const reviewerIdentifier = reviewUserId || reviewUserName || "unknown-reviewer";
    const reviewNumericId = hashStringToPositiveInt(`${movieId}:${reviewerIdentifier}`);
    const flaggerId = coerceNumericId(currentUserObj.backendId ?? currentUserObj.id, currentUserObj.id);
    const flaggedUserId = targetUser
      ? coerceNumericId(targetUser.backendId ?? targetUser.id, targetUser.id)
      : hashStringToPositiveInt(reviewerIdentifier);

    const response = await fetch(`${API_BASE_URL}/flags`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      },
      body: JSON.stringify({
        review_id: reviewNumericId,
        flagger_id: flaggerId,
        flagged_user_id: flaggedUserId,
        reason: trimmedReason,
      }),
    });

    let payload: any = {};
    try {
      payload = await response.json();
    } catch {
      payload = {};
    }

    if (!response.ok) {
      throw new Error(payload?.detail || "Unable to submit this flag right now.");
    }

    if (targetUser) {
      setUsers((prev) =>
        prev.map((u) =>
          u.id === targetUser.id ? { ...u, isFlagged: true, flagReason: trimmedReason } : u
        )
      );
    }

    return payload;
  };

  const handleMovieClick = (movie: Movie) => {
    setSelectedMovie(movie);
    setIsSuggestionsOpen(false);
    setActiveSection("movie-detail");
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

  const handleAddPenalty = async (userId: string, reason: string) => {
    if (!currentUserObj) {
      throw new Error("Please sign in to administer penalties.");
    }

    const targetUser = users.find((u) => u.id === userId);
    if (!targetUser) {
      throw new Error("Selected user could not be found.");
    }

    const trimmedReason = reason.trim();
    if (!trimmedReason) {
      throw new Error("Penalty reason is required.");
    }

    const payload: Record<string, unknown> = {
      user_id: targetUser.numericId,
      issued_by: currentUserObj.numericId,
      reason: trimmedReason,
    };

    const response = await fetch(`${API_BASE_URL}/penalties`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    let data: any = null;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      const message = data?.detail || "Unable to issue penalty right now.";
      throw new Error(message);
    }

    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, penalties: u.penalties + 1 } : u
      )
    );

    return data;
  };

  const handleRemovePenalty = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, penalties: Math.max(0, u.penalties - 1) } : u
      )
    );
  };

  const currentWatchlist = watchlists[currentUserId] || [];
  const showDiscoverySections = activeSection === "home" && filterGenre === "all";

  // Get all unique genres
  const allGenres = Array.from(new Set(movies.flatMap((movie) => movie.genre)));

  const filteredMovies = movies
    .filter((movie) => {
      const matchesGenre = filterGenre === "all" || movie.genre.includes(filterGenre);
      const matchesSearch =
        activeSection === "watchlist"
          ? movie.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            movie.genre.some((g) => g.toLowerCase().includes(searchQuery.toLowerCase()))
          : true;

      if (activeSection === "watchlist") {
        return matchesSearch && matchesGenre && currentWatchlist.includes(movie.id);
      }

      return matchesGenre;
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

  const movieReviews = useMemo(
    () => (selectedMovie ? reviews.filter((r) => r.id === selectedMovie.id) : []),
    [reviews, selectedMovie?.id]
  );

  const detailReleaseDate =
    selectedMovieMeta?.datePublished ||
    selectedMovie?.year ||
    selectedMovieMeta?.releaseDate ||
    "N/A";

  const detailDurationRaw =
    parseDurationMinutes(
      selectedMovieMeta?.duration ||
        selectedMovieMeta?.runtime ||
        selectedMovieMeta?.movieDuration ||
        selectedMovieMeta?.movieRuntime
    ) || 0;
  const detailDuration =
    detailDurationRaw > 0
      ? formatDuration(detailDurationRaw)
      : selectedMovieMeta && selectedMovieMeta.duration
      ? formatDuration(selectedMovieMeta.duration)
      : "N/A";

  const detailRating =
    toNumber(selectedMovieMeta?.movieIMDbRating, 0) ||
    toNumber(selectedMovieMeta?.userRatingAverage, 0) ||
    (selectedMovieMeta?.userRatingTotal && selectedMovieMeta?.userRatingCount
      ? toNumber(selectedMovieMeta.userRatingTotal / selectedMovieMeta.userRatingCount, 0)
      : 0) ||
    toNumber(selectedMovie?.rating, 0);

  const detailUserReviews =
    parseCount(selectedMovieMeta?.totalUserReviews) ||
    parseCount(selectedMovieMeta?.userRatingCount) ||
    parseCount(selectedMovieMeta?.totalRatingCount) ||
    parseCount(selectedMovie?.ratingCount);
  const trailerUrl = selectedMovie ? computeTrailerUrl(selectedMovieMeta, selectedMovie.title) : "";

  const displayTitle =
    activeSection === "home"
      ? "Latest Movies"
      : activeSection === "watchlist"
      ? "My Watchlist"
      : activeSection.toUpperCase();

  if (!isAuthenticated && (activeSection === "login" || activeSection === "register")) {
    if (authMode === "register") {
      return (
        <RegisterScreen
          onRegister={(data) => {
            setAuthError(null);
            const emailTaken = users.some((u) => u.email.toLowerCase() === data.email.toLowerCase());
            if (emailTaken) {
              setAuthError("An account already exists with that email.");
              return;
            }

            const baseId = slugify(data.name);
            let uniqueId = baseId;
            let suffix = 1;
            while (users.some((u) => u.id === uniqueId)) {
              uniqueId = `${baseId}-${suffix++}`;
            }

            const newUser: User = {
              id: uniqueId,
              name: data.name,
              email: data.email,
              password: data.password,
              joinDate: new Date().toISOString().split("T")[0],
              isFlagged: false,
              penalties: 0,
              isAdmin: data.isAdmin,
              numericId: hashStringToPositiveInt(uniqueId),
            };
            setUsers((prev) => [...prev, newUser]);
            setCurrentUser(data.name);
            setIsAuthenticated(true);
            setAuthMode("login");
            setActiveSection("home");
          }}
          onSwitchToLogin={() => {
            setAuthMode("login");
            setAuthError(null);
            setActiveSection("login");
          }}
          errorMessage={authError}
        />
      );
    }

    return (
      <LoginScreen
        onLogin={async ({ email, password }) => {
          setAuthError(null);
          const identifier = email.trim();

          try {
            const usernameForLogin = await resolveUsernameForLogin(identifier);
            const params = new URLSearchParams({
              username: usernameForLogin,
              password,
            });
            const response = await fetch(`${API_BASE_URL}/users/login?${params.toString()}`, {
              method: "POST",
            });
            const payload = await response.json();
            if (!response.ok) {
              throw new Error(payload?.detail || "Unable to log in. Please check your credentials.");
            }

            const backendUser = mapBackendUser(payload.user);
            const tokenRole = decodeRoleFromToken(payload.token);
            const fallbackUser = usersRef.current.find(
              (u) =>
                u.email.toLowerCase() === backendUser.email.toLowerCase() ||
                u.name.toLowerCase() === backendUser.name.toLowerCase()
            );
            const mergedUser: User = {
              ...fallbackUser,
              ...backendUser,
              isAdmin:
                tokenRole === "admin" ||
                fallbackUser?.isAdmin ||
                backendUser.isAdmin,
            };

            setAuthToken(payload.token);
            setCurrentUser(mergedUser.name);
            setIsAuthenticated(true);
            setActiveSection("home");
            setUsers((prev) => {
              const existing = prev.find((u) => u.name.toLowerCase() === mergedUser.name.toLowerCase());
              if (existing) {
                return prev.map((u) => (u.name.toLowerCase() === mergedUser.name.toLowerCase() ? mergedUser : u));
              }
              return [...prev, mergedUser];
            });
          } catch (error) {
            const message = error instanceof Error ? error.message : "Login failed. Please try again.";
            setAuthError(message);
          }
        }}
        onSwitchToRegister={() => {
          setAuthMode("register");
          setAuthError(null);
          setActiveSection("register");
        }}
        onBack={() => {
          setActiveSection("home");
          setAuthError(null);
        }}
        errorMessage={authError}
      />
    );
  }

  return (
    <div className="flex h-screen bg-neutral-950 text-white">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={(section) => {
          if (section === "admin" && !isAdmin) {
            setActiveSection("home");
            return;
          }
          if (!isAuthenticated && section === "watchlist") {
            setActiveSection("login");
            setAuthMode("login");
            return;
          }
          setActiveSection(section);
        }}
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
          ) : activeSection === "movie-detail" && selectedMovie ? (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-4xl font-semibold mb-2">{selectedMovie.title}</h1>
                  <div className="text-neutral-400">
                    <span className="mr-4">Release: {detailReleaseDate}</span>
                    <span>Duration: {detailDuration}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-neutral-400 text-sm">User Rating</p>
                  <p className="text-3xl text-yellow-400 font-semibold">{detailRating.toFixed(1)}</p>
                  <p className="text-neutral-400 text-sm mt-1">
                    User Reviews: {formatCompactNumber(detailUserReviews)}
                  </p>
                </div>
              </div>

              <div className="flex flex-col md:flex-row gap-4 items-start">
                <div className="w-full md:w-[38%]">
                  <div className="overflow-hidden h-[400px] md:h-[460px] bg-black">
                    <img
                      src={selectedMovie.poster}
                      alt={selectedMovie.title}
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
                <div className="w-full md:flex-1">
                  <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden h-[400px] md:h-[460px]">
                    {trailerUrl ? (
                      <iframe
                        src={trailerUrl}
                        title={`${selectedMovie.title} trailer`}
                        className="w-full h-full"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                    ) : (
                      <div className="w-full h-full bg-neutral-800 flex items-center justify-center text-neutral-500">
                        Trailer not available
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="w-full">
                <Button
                  variant="secondary"
                  className="w-full"
                  onClick={() => handleWatchlistToggle(selectedMovie.id)}
                >
                  {currentWatchlist.includes(selectedMovie.id) ? "Remove from Watchlist" : "Add to Watchlist"}
                </Button>
              </div>

              <div className="space-y-3">
                <h2 className="text-2xl font-semibold">Overview</h2>
                <p className="text-neutral-300 leading-relaxed">
                  {selectedMovie.description || "No description available."}
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold">Reviews</h2>
                  <span className="text-neutral-400 text-sm">{movieReviews.length} reviews</span>
                </div>
                <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span>Your rating:</span>
                    <div className="flex gap-1 flex-wrap">
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                        <button
                          key={rating}
                          type="button"
                          onClick={() => setDetailReviewInput((prev) => ({ ...prev, rating }))}
                          className={`w-9 h-9 rounded ${
                            rating <= detailReviewInput.rating
                              ? "bg-yellow-500 text-black"
                              : "bg-neutral-800 text-neutral-400"
                          }`}
                        >
                          {rating}
                        </button>
                      ))}
                    </div>
                  </div>
                  <Textarea
                    value={detailReviewInput.comment}
                    onChange={(e) => setDetailReviewInput((prev) => ({ ...prev, comment: e.target.value }))}
                    placeholder="Share your thoughts..."
                    className="bg-neutral-950 border-neutral-800"
                  />
                  <Button onClick={handleSubmitDetailReview}>Submit Review</Button>
                </div>

                <div className="space-y-3">
                  {movieReviews.length === 0 && (
                    <div className="text-neutral-500 text-sm">No reviews yet.</div>
                  )}
                  {movieReviews.map((review, index) => (
                    <div key={`${review.userId}-${index}`} className="border border-neutral-800 rounded-lg p-4 bg-neutral-900">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-sm">
                            {review.userName.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm">{review.userName}</p>
                            <p className="text-xs text-neutral-500">{review.date}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 text-yellow-400">
                          <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                          <span className="font-semibold">{review.rating}/10</span>
                        </div>
                      </div>
                      <p className="text-neutral-300">{review.comment}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : activeSection === "search" ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl mb-1">Search results for “{searchQuery.trim() || "…"}”</h2>
                  <p className="text-neutral-400">
                    {isSearching
                      ? "Searching..."
                      : `${searchResultsTotal} result${searchResultsTotal === 1 ? "" : "s"}`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="bg-neutral-900 border-neutral-800 text-white gap-2">
                        Sort: {searchSortBy === "title" ? "Title" : searchSortBy === "rating" ? "User Rating" : "Year"}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-neutral-900 border-neutral-800 text-white">
                      <DropdownMenuItem onClick={() => fetchSearchResults(searchQuery, { sortBy: "title" })}>
                        Title
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => fetchSearchResults(searchQuery, { sortBy: "rating" })}>
                        User Rating
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => fetchSearchResults(searchQuery, { sortBy: "year" })}>
                        Release Year
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                  <Button
                    variant="outline"
                    className="bg-neutral-900 border-neutral-800 text-white"
                    onClick={() => {
                      const next = searchSortOrder === "asc" ? "desc" : "asc";
                      fetchSearchResults(searchQuery, { sortOrder: next });
                    }}
                  >
                    Order: {searchSortOrder === "asc" ? "Asc" : "Desc"}
                  </Button>
                </div>
              </div>

              {searchError && (
                <div className="rounded border border-red-800 bg-red-900/30 px-4 py-3 text-red-200">
                  {searchError}
                </div>
              )}

              {isSearching && searchResults.length === 0 && (
                <div className="text-neutral-400">Loading search results...</div>
              )}

              {!isSearching && searchResults.length === 0 && !searchError && (
                <div className="text-neutral-400">No movies found. Try a different title.</div>
              )}

              {searchResults.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                  {searchResults.map((movie) => (
                    <MovieCard
                      key={movie.id}
                      movie={movie}
                      isInWatchlist={currentWatchlist.includes(movie.id)}
                      onWatchlistToggle={handleWatchlistToggle}
                      onMovieClick={handleMovieClick}
                    />
                  ))}
                </div>
              )}
            </div>
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
                  onFocus={() => setIsSuggestionsOpen(Boolean(searchQuery.trim()))}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleSearchSubmit();
                    }
                  }}
                      className="pl-10 bg-neutral-900 border-neutral-800 text-white placeholder:text-neutral-500"
                    />
                {isSuggestionsOpen && (
                  <div className="absolute left-0 right-0 mt-2 rounded-lg border border-neutral-800 bg-neutral-900 shadow-lg z-20 max-h-80 overflow-auto">
                    {isSuggestionsLoading ? (
                      <div className="px-4 py-3 text-sm text-neutral-400">Searching...</div>
                    ) : searchSuggestions.length === 0 ? (
                      <div className="px-4 py-3 text-sm text-neutral-500">No matches found.</div>
                    ) : (
                      searchSuggestions.map((movie) => (
                        <button
                          key={movie.id}
                          className="w-full text-left px-4 py-3 hover:bg-neutral-800 flex items-center justify-between"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => {
                            setSearchQuery(movie.title);
                            handleSearchSubmit(movie.title);
                          }}
                        >
                          <div>
                            <div className="text-sm">{movie.title}</div>
                            <div className="text-xs text-neutral-500">
                              {movie.year} • {movie.genre?.[0] ?? "Genre"}
                            </div>
                          </div>
                          <span className="text-xs text-yellow-500">{movie.rating.toFixed(1)}</span>
                        </button>
                      ))
                    )}
                  </div>
                )}
                  </div>
                  <div className="ml-4">
                    {isAuthenticated ? (
                      <UserSwitcher
                        currentUser={currentUser}
                        currentUserEmail={currentUserObj?.email}
                        onSignOut={() => {
                          setIsAuthenticated(false);
                          setAuthMode("login");
                          setAuthError(null);
                          setActiveSection("home");
                          setAuthToken(null);
                        }}
                      />
                    ) : (
                      <Button
                        variant="outline"
                        className="bg-neutral-900 border-neutral-800 text-white"
                        onClick={() => {
                          setActiveSection("login");
                          setAuthMode("login");
                        }}
                      >
                        Login / Register
                      </Button>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  
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

              {showDiscoverySections && (
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

              {(activeSection === "watchlist" || filterGenre !== "all") && (
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

    </div>
  );
}
