import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import DashboardLayout from "@/src/components/layout/DashboardLayout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Nadakki AI Enterprise Suite",
  description: "Plataforma Multi-Tenant con 276 Agentes IA Especializados",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body suppressHydrationWarning className={inter.className} style={{ margin: 0, padding: 0 }}>
        <DashboardLayout>
          {children}
        </DashboardLayout>
      </body>
    </html>
  );
}


