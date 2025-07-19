'use client'
import React from "react";
import { usePlatformConfig } from "@/shared/contexts/PlatformConfigContext";

export function Footer() {
  const { platformConfig } = usePlatformConfig();

  return (
    <footer className="py-4 px-4 sm:px-6 text-center sm:text-end max-w-7xl mx-auto text-xs">
      © 2025 {platformConfig?.name}. All rights reserved.
    </footer>
  );
}
