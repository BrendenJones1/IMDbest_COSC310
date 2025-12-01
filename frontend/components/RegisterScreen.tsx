import { useState } from "react";
import { Film, Mail, Lock, User, Eye, EyeOff, Shield, UserCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Checkbox } from "./ui/checkbox";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";

interface RegisterScreenProps {
  onRegister?: (data: { name: string; email: string; password: string; isAdmin: boolean }) => void;
  onSwitchToLogin?: () => void;
  errorMessage?: string | null;
}

export function RegisterScreen({ onRegister, onSwitchToLogin, errorMessage }: RegisterScreenProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [role, setRole] = useState<"user" | "admin">("user");
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    if (!agreedToTerms) {
      newErrors.terms = "You must agree to the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      if (onRegister) {
        onRegister({ name, email, password, isAdmin: role === "admin" });
      } else {
        // Demo mode
        alert(`Account created for ${name}!\\nEmail: ${email}\\nRole: ${role === "admin" ? "Admin" : "User"}\\n\\nIn production, this would create a real account.`);
      }
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center">
            <Film className="h-6 w-6 text-white" />
          </div>
          <span className="text-white tracking-tight text-2xl">IMDB</span>
        </div>

        {/* Register Card */}
        <div className="bg-neutral-900 rounded-lg border border-neutral-800 p-8">
          <div className="mb-6">
            <h1 className="text-white text-2xl mb-2">Create an account</h1>
            <p className="text-neutral-400 text-sm">
              Join IMDB to start reviewing your favorite movies
            </p>
          </div>

          {errorMessage && (
            <div className="mb-4 rounded border border-red-900 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role Selection */}
            <div className="space-y-3">
              <Label className="text-white">Account Type</Label>
              <RadioGroup value={role} onValueChange={(value) => setRole(value as "user" | "admin")}>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2 flex-1 p-3 rounded-lg border border-neutral-700 bg-neutral-800/50 hover:border-neutral-600 transition-colors cursor-pointer">
                    <RadioGroupItem value="user" id="user" className="border-neutral-600 text-red-600" />
                    <Label htmlFor="user" className="flex items-center gap-2 text-white cursor-pointer flex-1">
                      <UserCircle className="h-5 w-5 text-neutral-400" />
                      <div>
                        <div>User</div>
                        <div className="text-xs text-neutral-400">Browse and review movies</div>
                      </div>
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2 flex-1 p-3 rounded-lg border border-neutral-700 bg-neutral-800/50 hover:border-neutral-600 transition-colors cursor-pointer">
                    <RadioGroupItem value="admin" id="admin" className="border-neutral-600 text-red-600" />
                    <Label htmlFor="admin" className="flex items-center gap-2 text-white cursor-pointer flex-1">
                      <Shield className="h-5 w-5 text-neutral-400" />
                      <div>
                        <div>Admin</div>
                        <div className="text-xs text-neutral-400">Manage users and content</div>
                      </div>
                    </Label>
                  </div>
                </div>
              </RadioGroup>
            </div>

            {/* Name Field */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-white">
                Name
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="pl-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                />
              </div>
              {errors.name && (
                <p className="text-red-400 text-sm">{errors.name}</p>
              )}
            </div>

            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white">
                Email
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                />
              </div>
              {errors.email && (
                <p className="text-red-400 text-sm">{errors.email}</p>
              )}
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-white">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 pr-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-400"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-400 text-sm">{errors.password}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-white">
                Confirm Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pl-10 pr-10 bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-400"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-red-400 text-sm">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Terms and Conditions */}
            <div className="flex items-start gap-2">
              <Checkbox
                id="terms"
                checked={agreedToTerms}
                onCheckedChange={(checked) => setAgreedToTerms(checked as boolean)}
                className="mt-1 border-neutral-700 data-[state=checked]:bg-red-600 data-[state=checked]:border-red-600"
              />
              <label
                htmlFor="terms"
                className="text-sm text-neutral-400 leading-tight cursor-pointer"
              >
                I agree to the{" "}
                <a href="#" className="text-red-400 hover:text-red-300">
                  Terms of Service
                </a>{" "}
                and{" "}
                <a href="#" className="text-red-400 hover:text-red-300">
                  Privacy Policy
                </a>
              </label>
            </div>
            {errors.terms && (
              <p className="text-red-400 text-sm">{errors.terms}</p>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white"
            >
              Create Account
            </Button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-neutral-400 text-sm">
              Already have an account?{" "}
              <button
                onClick={onSwitchToLogin}
                className="text-red-400 hover:text-red-300"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>

        {/* Footer Note */}
        <p className="text-center text-neutral-500 text-xs mt-6">
          This is a demo app. No real data is collected.
        </p>
      </div>
    </div>
  );
}
