"use client";

import { Wifi, Video, Settings, House } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Home", icon: House, path: "/" },
    { name: "Live", icon: Wifi, path: "/live" },
    { name: "Playback", icon: Video, path: "/playback" },
    { name: "Settings", icon: Settings, path: "/settings" },
  ];

  return (
    <aside className="w-48 bg-white border-r border-gray-200 flex flex-col items-center py-10">
      <nav className="flex flex-col items-start gap-8 text-lg font-medium text-gray-800">
        {navItems.map(({ name, icon: Icon, path }) => {
          const isActive = pathname === path;
          return (
            <Link
              key={name}
              href={path}
              className={`flex items-center gap-3 transition ${
                isActive ? "text-[#FF5A5F]" : "hover:text-[#FF5A5F]"
              }`}
            >
              <Icon size={24} />
              <span>{name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
