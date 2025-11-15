import { useState } from "react";
import { Film, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

const demoCredentials = [
  { label: "Demo Admin", email: "admin@demo.com", password: "password" },
  { label: "Demo User", email: "user@demo.com", password: "password" },
];

interface LoginScreenProps {
  onLogin?: (data: { email: string; password: string }) => void;
  onSwitchToRegister?: () => void;
  errorMessage?: string | null;
  isSubmitting?: boolean;
}

export function LoginScreen({
  onLogin,
  onSwitchToRegister,
  errorMessage,
  isSubmitting = false,
}: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onLogin?.({ email, password });
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center">
            <Film className="h-6 w-6 text-white" />
          </div>
          <span className="text-white tracking-tight text-2xl">IMDB</span>
        </div>

        <div className="bg-neutral-900 rounded-lg border border-neutral-800 p-8">
          <div className="mb-6">
            <h1 className="text-white text-2xl mb-2">Welcome back</h1>
            <p className="text-neutral-400 text-sm">Sign in to continue rating and managing movies</p>
          </div>

          <div className="bg-neutral-800/70 border border-neutral-700 rounded-lg p-4 mb-6 text-sm text-neutral-300">
            <p className="text-white text-xs uppercase tracking-wide mb-2">Demo credentials</p>
            <div className="space-y-1">
              {demoCredentials.map((cred) => (
                <div key={cred.email} className="flex flex-wrap gap-x-4 gap-y-1">
                  <span className="font-medium text-white">{cred.label}</span>
                  <span>Email: <code className="text-red-300">{cred.email}</code></span>
                  <span>Password: <code className="text-red-300">{cred.password}</code></span>
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white">
                Email
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-white">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 pr-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                  required
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500"
                  onClick={() => setShowPassword((prev) => !prev)}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {errorMessage && (
              <p className="text-red-400 text-sm text-center">{errorMessage}</p>
            )}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <div className="text-center mt-6">
            <p className="text-neutral-400 text-sm">
              Don't have an account?{" "}
              <button
                type="button"
                className="text-red-400 hover:text-red-300"
                onClick={onSwitchToRegister}
              >
                Create one
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
