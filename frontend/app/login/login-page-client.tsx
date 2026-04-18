"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Eye, EyeOff, LogIn, Loader2, ArrowLeftRight, Store, TrendingUp } from "lucide-react";
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

function LiveStat({
  value,
  label,
  icon,
  flash,
}: {
  value: string | number;
  label: string;
  icon: React.ReactNode;
  flash: boolean;
}) {
  return (
    <div className="bg-white/55 dark:bg-gray-900/55 backdrop-blur-md rounded-xl p-4 border border-white/30 dark:border-gray-700/30 shadow-sm">
      <div className="flex items-center gap-1.5 mb-2 text-muted-foreground">{icon}</div>
      <div
        className={`text-2xl font-bold tabular-nums transition-colors duration-300 ${
          flash ? "text-blue-600 dark:text-blue-400" : "text-gray-900 dark:text-white"
        }`}
      >
        {typeof value === "number" ? value.toLocaleString("nl-NL") : value}
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 leading-snug">{label}</div>
    </div>
  );
}

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
  const [mounted, setMounted] = useState(false);

  // Live counters
  const [articlesCount, setArticlesCount] = useState(1847);
  const [redistributionsCount, setRedistributionsCount] = useState(63);
  const [articleFlash, setArticleFlash] = useState(false);
  const [redisFlash, setRedisFlash] = useState(false);
  const articleFlashTimer = useRef<ReturnType<typeof setTimeout>>();
  const redisFlashTimer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => { setMounted(true); }, []);

  useEffect(() => {
    if (isAuthenticated && !authLoading) router.push(returnUrl || "/");
  }, [isAuthenticated, authLoading, router, returnUrl]);

  useEffect(() => {
    const articleInterval = setInterval(() => {
      setArticlesCount(prev => prev + 1);
      setArticleFlash(true);
      clearTimeout(articleFlashTimer.current);
      articleFlashTimer.current = setTimeout(() => setArticleFlash(false), 400);
    }, 4200);

    const redisInterval = setInterval(() => {
      setRedistributionsCount(prev => prev + 1);
      setRedisFlash(true);
      clearTimeout(redisFlashTimer.current);
      redisFlashTimer.current = setTimeout(() => setRedisFlash(false), 400);
    }, 13000);

    return () => {
      clearInterval(articleInterval);
      clearInterval(redisInterval);
      clearTimeout(articleFlashTimer.current);
      clearTimeout(redisFlashTimer.current);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!username.trim()) { setError("Gebruikersnaam is verplicht"); return; }
    if (!password) { setError("Wachtwoord is verplicht"); return; }

    setIsLoading(true);
    try {
      await login({ username: username.trim(), password, remember_me: rememberMe });
      toast({ title: "Inloggen geslaagd!", description: "Je wordt doorgestuurd naar het dashboard..." });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Inloggen mislukt. Controleer je gebruikersnaam en wachtwoord.";
      setError(errorMessage);
      toast({ variant: "destructive", title: "Inloggen mislukt", description: errorMessage });
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
    <div className="min-h-screen relative flex">
      <NetworkBackground />

      {/* Left info panel — desktop only */}
      <div
        className={`hidden md:flex flex-col justify-center flex-1 px-12 xl:px-20 relative z-10 transition-all duration-700 ease-out ${
          mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        }`}
      >
        {/* Branding */}
        <div className="mb-10">
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-2.5 inline-block shadow-sm mb-6">
            <Image
              src="/mc-company-logo.png"
              alt="MC Company"
              width={150}
              height={118}
              priority
              className="h-auto w-[72px] object-contain"
            />
          </div>
          <h1 className="text-3xl xl:text-4xl font-bold text-gray-900 dark:text-white mb-3 leading-tight">
            Digital Resupplying Tool
          </h1>
          <p className="text-base xl:text-lg text-gray-600 dark:text-gray-300 max-w-sm leading-relaxed">
            Slimme artikelherverdeling voor uw filiaalnetwerk — automatisch, transparant en efficiënt.
          </p>
        </div>

        {/* Live stats */}
        <div className="grid grid-cols-3 gap-3 max-w-md">
          <LiveStat
            value={articlesCount}
            label="artikelen herverdeeld"
            icon={<TrendingUp className="w-3.5 h-3.5" />}
            flash={articleFlash}
          />
          <LiveStat
            value={10}
            label="filialen verbonden"
            icon={<Store className="w-3.5 h-3.5" />}
            flash={false}
          />
          <LiveStat
            value={redistributionsCount}
            label="redistributies vandaag"
            icon={<ArrowLeftRight className="w-3.5 h-3.5" />}
            flash={redisFlash}
          />
        </div>
      </div>

      {/* Right login panel */}
      <div className="flex items-center justify-center w-full md:w-auto md:min-w-[440px] p-5 md:p-8 relative z-20">
        <div
          className={`w-full max-w-sm transition-all duration-700 delay-150 ease-out ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
          }`}
        >
          {/* Subtle glow ring around card */}
          <div className="relative">
            <div className="absolute -inset-px rounded-2xl bg-gradient-to-br from-blue-400/20 via-transparent to-emerald-400/20 dark:from-blue-500/25 dark:to-emerald-500/25 pointer-events-none" />
            <Card className="relative shadow-2xl bg-white/72 dark:bg-gray-900/72 backdrop-blur-2xl border-white/40 dark:border-gray-700/40 shadow-[0_8px_60px_rgba(59,130,246,0.13),0_2px_12px_rgba(0,0,0,0.07)] rounded-2xl">
              <CardHeader className="space-y-3 pb-4">
                <div className="flex flex-col items-center">
                  {/* Logo — shown in card on mobile, hidden on desktop (shown in left panel) */}
                  <div className="md:hidden bg-white dark:bg-gray-800 rounded-lg p-2 mb-3 shadow-sm">
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
                      className="w-full bg-white/60 dark:bg-gray-800/60"
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
                        className="w-full pr-10 bg-white/60 dark:bg-gray-800/60"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                        tabIndex={-1}
                        disabled={isLoading}
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
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
                    <Label htmlFor="remember" className="text-sm font-normal cursor-pointer select-none">
                      Onthoud mij (30 dagen)
                    </Label>
                  </div>

                  {error && (
                    <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20">
                      <p className="text-sm text-destructive">{error}</p>
                    </div>
                  )}

                  <Button type="submit" className="w-full" disabled={isLoading} size="lg">
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
                  <div className="mt-4 p-3 rounded-md bg-muted/50 border border-border">
                    <p className="text-xs font-semibold mb-2 text-muted-foreground">Test Credentials:</p>
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
        </div>
      </div>
    </div>
  );
}
