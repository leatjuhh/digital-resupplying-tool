import { LoginPageClient } from "./login-page-client";

type LoginPageProps = {
  searchParams?: {
    returnUrl?: string | string[];
  };
};

export default function LoginPage({ searchParams }: LoginPageProps) {
  const rawReturnUrl = searchParams?.returnUrl;
  const returnUrl = Array.isArray(rawReturnUrl) ? rawReturnUrl[0] : rawReturnUrl;

  return <LoginPageClient returnUrl={returnUrl} />;
}
