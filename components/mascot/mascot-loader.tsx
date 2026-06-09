"use client";
import { useEffect, useState } from "react";
import MascotPet from "./mascot-pet";

export function MascotLoader() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return null;

  return <MascotPet />;
}
