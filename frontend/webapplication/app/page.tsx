"use client";

import Sidebar from "./components/sidebar";
import Image from "next/image";

export default function HomePage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 flex flex-col items-center justify-start py-10 px-6 bg-gray-50">
        <div className="mb-8">
          <Image
            src="/guard_car_logo.png"
            alt="GuardCar Logo"
            width={220}
            height={220}
            priority
          />
        </div>

        <section className="max-w-xl text-center mb-10">
          <h1 className="text-3xl font-extrabold mb-4 text-black">Our Vision</h1>
          <p className="text-gray-700 leading-relaxed">
            GuardCar is an AI-powered vehicle security system that monitors your car in
            real time, detects suspicious activity, and sends instant alerts so you never
            miss a thing.
          </p>
        </section>

        <section className="bg-[#FF5A5F] text-white rounded-2xl px-8 py-6 max-w-md text-center">
          <h2 className="text-xl font-semibold mb-3">Key Features</h2>
          <ul className="space-y-2 text-sm font-medium">
            <li>Multi-camera 24/7 monitoring</li>
            <li>AI-powered detection & tracking</li>
            <li>Instant alerts via SMS & email</li>
            <li>Secure video storage & dashboard</li>
          </ul>
        </section>
      </main>
    </div>
  );
}