'use client';

/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 * Optionally checks for specific permissions
 */

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/auth-context';

interface ProtectedRouteProps {
  children: React.ReactNode;
  permission?: string;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ 
  children, 
  permission, 
  fallback 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, hasPermission } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Don't redirect if still loading auth state
    if (isLoading) return;

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      const returnUrl = encodeURIComponent(pathname);
      router.push(`/login?returnUrl=${returnUrl}`);
    }
  }, [isAuthenticated, isLoading, router, pathname]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Authenticatie controleren...
            </p>
          </div>
        </div>
      )
    );
  }

  // Don't render anything if not authenticated (redirect will happen)
  if (!isAuthenticated) {
    return null;
  }

  // Check permission if specified
  if (permission && !hasPermission(permission)) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-2">Geen Toegang</h2>
          <p className="text-muted-foreground mb-4">
            Je hebt geen toegang tot deze pagina. Neem contact op met een administrator als je denkt dat dit een fout is.
          </p>
          <p className="text-sm text-muted-foreground">
            Vereiste permissie: <code className="font-mono bg-muted px-2 py-1 rounded">{permission}</code>
          </p>
        </div>
      </div>
    );
  }

  // Render children if authenticated and has permission
  return <>{children}</>;
}
