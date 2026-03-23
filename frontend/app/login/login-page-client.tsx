"use client";

/**
 * Login Page
 * Professional login interface with MC Company branding
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Eye, EyeOff, LogIn, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { useToast } from "@/hooks/use-toast";
import { NetworkBackground } from "@/components/auth/network-background";

type LoginPageClientProps = {
  returnUrl?: string;
};

export function LoginPageClient({ returnUrl }: LoginPageClientProps) {
  const router = useRouter();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const { toast } = useToast();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      router.push(returnUrl || "/");
    }
  }, [isAuthenticated, authLoading, router, returnUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!username.trim()) {
      setError("Gebruikersnaam is verplicht");
      return;
    }

    if (!password) {
      setError("Wachtwoord is verplicht");
      return;
    }

    setIsLoading(true);

    try {
      await login({
        username: username.trim(),
        password,
        remember_me: rememberMe,
      });

      toast({
        title: "Inloggen geslaagd!",
        description: "Je wordt doorgestuurd naar het dashboard...",
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Inloggen mislukt. Controleer je gebruikersnaam en wachtwoord.";

      setError(errorMessage);

      toast({
        variant: "destructive",
        title: "Inloggen mislukt",
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Authenticatie controleren...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center md:justify-end p-4 md:pr-16 relative">
      <NetworkBackground />

      <Card className="w-full max-w-sm shadow-2xl relative z-20 bg-white/65 dark:bg-gray-900/65 backdrop-blur-2xl border-white/30 dark:border-gray-700/30">
        <CardHeader className="space-y-3 pb-4">
          <div className="flex flex-col items-center">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-2 mb-3 shadow-sm">
              <Image
                src="/mc-company-logo.png"
                alt="MC Company"
                width={150}
                height={118}
                priority
                className="h-auto w-[60px] object-contain"
              />
            </div>
            <CardTitle className="text-xl font-bold text-center">
              Digital Resupplying Tool
            </CardTitle>
            <CardDescription className="text-center text-xs">
              Log in om door te gaan naar het dashboard
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="username" className="text-sm">Gebruikersnaam</Label>
              <Input
                id="username"
                type="text"
                placeholder="Voer je gebruikersnaam in"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
                autoComplete="username"
                autoFocus
                className="w-full"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-sm">Wachtwoord</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Voer je wachtwoord in"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  autoComplete="current-password"
                  className="w-full pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="remember"
                checked={rememberMe}
                onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                disabled={isLoading}
              />
              <Label
                htmlFor="remember"
                className="text-sm font-normal cursor-pointer select-none"
              >
                Onthoud mij (30 dagen)
              </Label>
            </div>

            {error && (
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
              size="lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Inloggen...
                </>
              ) : (
                <>
                  <LogIn className="mr-2 h-4 w-4" />
                  Inloggen
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Hulp nodig? Neem contact op met IT support
            </p>
          </div>

          {process.env.NODE_ENV === "development" && (
            <div className="mt-6 p-3 rounded-md bg-muted/50 border border-border">
              <p className="text-xs font-semibold mb-2 text-muted-foreground">
                Test Credentials:
              </p>
              <ul className="text-xs text-muted-foreground space-y-1">
                <li>Admin: admin / Admin123!</li>
                <li>User: user / User123!</li>
                <li>Store: store / Store123!</li>
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
