import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;

  const redirects: Record<string, string> = {
    "/google-ads": "/advertising/google-ads",
    "/meta-ads": "/advertising/meta-ads",
    "/linkedin-ads": "/advertising/linkedin-ads",
    "/tiktok-ads": "/advertising/tiktok-ads",
    "/unified": "/advertising/unified",
  };

  for (const [oldP, newP] of Object.entries(redirects)) {
    if (path === oldP || path.startsWith(oldP + "/")) {
      const newUrl = new URL(newP + path.slice(oldP.length), request.url);
      return NextResponse.redirect(newUrl, 307);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/google-ads/:path*",
    "/meta-ads/:path*",
    "/linkedin-ads/:path*",
    "/tiktok-ads/:path*",
    "/unified/:path*",
  ],
};
