"use client";
import { useEffect, useRef, useState } from "react";
import Sidebar from "../components/sidebar";
import { useRouter } from "next/navigation";



export default function LivePage() {

	// Check login
    const router = useRouter();
    useEffect(() => {
        const isLoggedIn = sessionStorage.getItem("loggedIn");
        if (!isLoggedIn) {
            router.push("/");
        }
    }, [router]);


    const videoRef = useRef<HTMLVideoElement>(null);


    // Fetch video list
    const [recentVideos, setRecentVideos] = useState<string[]>([]);
    useEffect(() => {
        const loadVideos = async () => {
            try {
                const res = await fetch("/api/videos");
                const data = await res.json();

                // Sort newest first (alphabetical → reverse)
                const sorted = data.sort().reverse();
                setRecentVideos(sorted.slice(0, 5));
            } catch (err) {
                console.error("Error loading videos:", err);
            }
        };

        loadVideos();
    }, []);


    // Structure:
	// left side nav bar full length of screen, width 48
	// main content area full length of screen, fill rest width
		// Title
		// video player
		// title
		// 5 video players
    return (
        <div className="flex min-w-screen bg-gray-50">
            <Sidebar />

            <div className="flex flex-col flex-1 bg-gray-100">
                <header className="w-full px-8 py-4 border-b border-gray-300 bg-white shadow-sm">
                    <h1 className="text-3xl font-semibold text-gray-800">Live View</h1>
                </header>

                <div className="flex flex-col items-center justify-start flex-1 bg-gray-100 py-10">
                    
                    {/* Main Live Stream Player */}
                    <div className="relative w-[1200px] h-[700px] bg-black rounded-2xl overflow-hidden shadow-lg flex items-center justify-center">
                        <video
                            ref={videoRef}
                            src="https://www.w3schools.com/html/mov_bbb.mp4"
                            className="w-full h-full object-cover rounded-2xl"
                            controls
                            muted
                            controlsList="nodownload"
                        />
                    </div>

                    {/* Recent Videos */}
                    <h2 className="text-2xl font-semibold mt-10 mb-4">
                        Most Recent Videos
                    </h2>

                    <div className="grid grid-cols-5 gap-6 w-[1200px]">
                        {recentVideos.length === 0 ? (
                            <p className="text-gray-600 col-span-5 text-center">
                                No videos found.
                            </p>
                        ) : (
                            recentVideos.map((file, idx) => (
                                <div
                                    key={idx}
                                    className="cursor-pointer flex flex-col items-center group"
                                >
                                    <video
                                        src={`/videos/${file}`}
                                        className="rounded-lg shadow-md border border-gray-300 w-[160px] h-[90px] object-cover"
                                        controls
                            			muted
                                    />

                                    <p className="text-center text-sm mt-2 text-gray-700 truncate w-full">
                                        {file}
                                    </p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}