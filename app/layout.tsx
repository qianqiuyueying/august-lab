import type { Metadata } from "next";
import { ConditionalNav } from "@/components/conditional-nav";
import { MascotLoader } from "@/components/mascot/mascot-loader";
import "./globals.css";

export const metadata: Metadata = {
  title: "August's Lab",
  description: "写点代码，拍点照片，偶尔做出点什么。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <ConditionalNav />
        <main>{children}</main>
        <MascotLoader />
      </body>
    </html>
  );
}
