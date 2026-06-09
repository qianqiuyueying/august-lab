"use client";
import dynamic from "next/dynamic";

const MascotPet = dynamic(() => import("./mascot-pet"), { ssr: false });

export function MascotLoader() {
  return <MascotPet />;
}
