import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Providers from "../components/Providers";

const bodyFont = Space_Grotesk({ subsets: ["latin"] });
const codeFont = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-code",
});

export const metadata = {
  title: "Market Hub | Gear for developers",
  description:
    "The marketplace for developers: laptops, keyboards, circuits and more.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${bodyFont.className} ${codeFont.variable} antialiased`}
      >
        <Providers>
          <Navbar />
          {children}
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
