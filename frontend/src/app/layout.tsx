import type { Metadata } from "next";
import { Press_Start_2P, Be_Vietnam_Pro } from "next/font/google";
import "./globals.css";

const pressStart2P = Press_Start_2P({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-press-start",
});

const beVietnamPro = Be_Vietnam_Pro({
  weight: ["400", "700"],
  subsets: ["vietnamese", "latin"],
  variable: "--font-be-vietnam",
});

export const metadata: Metadata = {
  title: "PixelParlament",
  description: "Agentic Governance System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className={`${pressStart2P.variable} ${beVietnamPro.variable} antialiased h-screen w-screen overflow-hidden`}>
        {children}
      </body>
    </html>
  );
}
