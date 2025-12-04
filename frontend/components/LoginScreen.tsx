import { useState } from "react";
import { Film, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

interface LoginScreenProps {
  onLogin?: (data: { email: string; password: string }) => void;
  onSwitchToRegister?: () => void;
  onBack?: () => void;
  errorMessage?: string | null;
}

const DEMO_ACCOUNTS = [
  { label: "Admin demo", email: "admin@demo.com", password: "password" },
  { label: "User demo", email: "user@demo.com", password: "password" },
];

export function LoginScreen({ onLogin, onSwitchToRegister, onBack, errorMessage }: LoginScreenProps) {
  const [selectedDemo, setSelectedDemo] = useState(DEMO_ACCOUNTS[0].email);
  const [email, setEmail] = useState(DEMO_ACCOUNTS[0].email);
  const [password, setPassword] = useState(DEMO_ACCOUNTS[0].password);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const nextErrors: { [key: string]: string } = {};

    if (!email.trim()) {
      nextErrors.email = "Email or username is required";
    }

    if (!password) {
      nextErrors.password = "Password is required";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }

    if (onLogin) {
      onLogin({ email, password });
    } else {
      alert(`Login attempt for ${email}.\nIn production this would authenticate against the backend.`);
    }
  };

  const handlePrefill = (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setErrors({});
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="mb-4 flex justify-start">
          {onBack && (
            <Button
              variant="ghost"
              className="text-neutral-300 hover:text-white"
              onClick={onBack}
            >
              ← Back to Home
            </Button>
          )}
        </div>
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center">
            <Film className="h-6 w-6 text-white" />
          </div>
          <span className="text-white tracking-tight text-2xl">IMDB</span>
        </div>

        <div className="bg-neutral-900 rounded-lg border border-neutral-800 p-8">
          <div className="mb-6">
            <h1 className="text-white text-2xl mb-2">Welcome back</h1>
            <p className="text-neutral-400 text-sm">Sign in to continue reviewing movies</p>
          </div>

          {errorMessage && (
            <div className="mb-4 rounded border border-red-900 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="login-email" className="text-white">
                Email or username
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="login-email"
                  type="text"
                  placeholder="Enter your email or username"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                />
              </div>
              {errors.email && <p className="text-red-400 text-sm">{errors.email}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="login-password" className="text-white">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 pr-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-400"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.password && <p className="text-red-400 text-sm">{errors.password}</p>}
            </div>

            <Button type="submit" className="w-full bg-red-600 hover:bg-red-700 text-white">
              Sign in
            </Button>
          </form>

          <div className="mt-6 space-y-2">
            <p className="text-sm text-neutral-300">
              Demo accounts (password: <span className="text-white font-semibold">password</span>)
            </p>
            <div className="grid gap-2">
              {DEMO_ACCOUNTS.map((account) => (
                <button
                  key={account.email}
                  type="button"
                  onClick={() => handlePrefill(account.email, account.password)}
                  className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-900 px-4 py-2 text-left text-sm text-white hover:bg-neutral-800 transition"
                >
                  <div>
                    <div className="font-medium">{account.label}</div>
                    <div className="text-xs text-neutral-400">{account.email}</div>
                  </div>
                  <span className="text-xs uppercase tracking-wide text-red-300">Demo</span>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 text-center text-sm text-neutral-400">
            <span>Need an account?</span>{" "}
            <button
              type="button"
              className="text-red-400 hover:text-red-300 font-medium"
              onClick={onSwitchToRegister}
            >
              Create one now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
