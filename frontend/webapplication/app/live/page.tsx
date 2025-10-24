"use client";
import { useEffect, useRef } from "react";
import Sidebar from "../components/sidebar";
import { useRouter } from "next/navigation";

// Functionality:
// Simple video player using native browser controls
// Button to start recording (To DO)
// Video Stram Source from server (To DO)
export default function LivePage() {

	// Check login
    const router = useRouter();
	useEffect(() => {
		const isLoggedIn = sessionStorage.getItem("loggedIn");
		if (!isLoggedIn){
			router.push("/");
		}
	}, [router]);

    const videoRef = useRef<HTMLVideoElement>(null);
	
	// Start recording (To Do)
    const startRecording = () => {
		
	};

    // Structure:
	// left side nave bar full length of screen, width 48
	// main content area centered
		// video player container with black background, rounded corners
		// button below to start recording	
	return (
		<div className="flex min-h-screen bg-gray-50">
			<Sidebar />

			<div className="flex flex-col items-center justify-center flex-1 bg-gray-100">
				<div className="relative w-[1200px] h-[700px] bg-black rounded-2xl overflow-hidden shadow-lg flex items-center justify-center">
					<video
						ref={videoRef}
						src="https://www.w3schools.com/html/mov_bbb.mp4" // get real source from server
						className="w-full h-full object-cover rounded-2xl"
						controls
						muted
                        controlsList="nodownload"
					/>
				</div>

				<div className="mt-6 flex gap-4">
					<button
						onClick={startRecording}
						className="px-6 py-3 bg-red-600 text-white rounded-lg shadow hover:bg-red-700 transition"
					>
						Start Recording (Server)
					</button>
				</div>
			</div>
		</div>
	);
}
