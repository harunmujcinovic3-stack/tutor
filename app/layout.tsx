import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SlaagZeker – Eindexamen bijles die werkt",
  description:
    "Persoonlijke begeleiding voor havo- en vwo-scholieren die zeker willen slagen voor hun eindexamen. Meld je aan voor de wachtlijst.",
  openGraph: {
    title: "SlaagZeker – Eindexamen bijles die werkt",
    description:
      "Persoonlijke begeleiding voor havo- en vwo-scholieren die zeker willen slagen voor hun eindexamen.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="nl" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
