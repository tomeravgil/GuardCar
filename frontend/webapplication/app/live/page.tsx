"use client";
import { useState, useRef } from "react";
import { FaPlay, FaPause, FaExpand } from "react-icons/fa";
import Sidebar from "../components/sidebar";
import { useEffect } from "react";
import { useRouter } from "next/navigation";


// Functionality:
// Video player with play/pause and fullscreen controls
// Button to start recording (To DO)
// Video Stram Source from server (To DO)
export default function LivePage() {


	const router = useRouter();
	useEffect(() => {
		const isLoggedIn = sessionStorage.getItem("loggedIn");
		if (!isLoggedIn) {
			router.push("/");
		}
	}, []);


  	const videoRef = useRef<HTMLVideoElement>(null);
  	const containerRef = useRef<HTMLDivElement>(null);
  	const [isPlaying, setIsPlaying] = useState(false);
  	const [showControls, setShowControls] = useState(false);


  	const togglePlay = () => {
		const video = videoRef.current;
		if (!video) return;

		if (isPlaying) {
			video.pause();
			setIsPlaying(false);
		} else {
			video.play()
			.then(() => setIsPlaying(true))
			.catch(err => console.log("Play blocked:", err));
		}
	};


  	const goFullscreen = () => {
		if (!document.fullscreenElement) {
			if (containerRef.current?.requestFullscreen) {
				containerRef.current.requestFullscreen();
			}
		} else {
			if (document.exitFullscreen) {
				document.exitFullscreen();
			}
		}
	};


	const startRecording = () => {
		// To Do
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
				<div
					ref={containerRef}
					className="relative w-[1200px] h-[700px] bg-black rounded-xl overflow-hidden"
					onMouseEnter={() => setShowControls(true)}
					onMouseLeave={() => setShowControls(false)}
				>
					<video
						ref={videoRef}
						className="w-full h-full object-cover"
						src="https://www.w3schools.com/html/mov_bbb.mp4" // need real camera source
					/>
					{showControls && (
						<div className="absolute bottom-0 left-0 right-0 bg-black/50 flex items-center justify-between p-3">
							<button
								onClick={togglePlay}
								className="text-white text-xl hover:scale-110 transition"
							>
								{isPlaying ? <FaPause /> : <FaPlay />}
							</button>

							<button
								onClick={goFullscreen}
								className="text-white text-xl hover:scale-110 transition"
							>
								<FaExpand />
							</button>
						</div>
					)}
				</div>
        
				<div className="mt-4 flex gap-4">
					<button className="px-4 py-2 bg-red-600 text-white rounded"
						onClick={startRecording}
					>
						Start Recording (Server)
					</button>
				</div>
      		</div>
    	</div>
  	);
}