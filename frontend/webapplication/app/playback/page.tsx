"use client";
import { useState, useEffect, useRef } from "react";
import Sidebar from "../components/sidebar";
import { useRouter } from "next/navigation";


export default function PlaybackPage() {

	//Check Logged In
	const router = useRouter();
	useEffect(() => {
		const isLoggedIn = sessionStorage.getItem("loggedIn");
		if (!isLoggedIn){
			router.push("/");
		}
	}, [router]);


  	const [videoFiles, setVideoFiles] = useState<string[]>([]);
  	const [page, setPage] = useState(0);
  	const pageSize = 20;
	

	// Fetch videos
	useEffect(() => {
		fetch("/api/videos")
		.then((res) => res.json())
		.then((data) => setVideoFiles(data))
		.catch((err) => console.error("Failed to load videos:", err));
	}, []);


	// Num of pages
	const totalPages = Math.ceil(videoFiles.length / pageSize);
	const startIndex = page * pageSize;
	const visibleVideos = videoFiles.slice(startIndex, startIndex + pageSize);

	const goNext = () => setPage((p) => Math.min(p + 1, totalPages - 1));
	const goPrev = () => setPage((p) => Math.max(p - 1, 0));


    // Structure:
	// left side nav bar full length of screen, width 48
	// main content area full length of screen, fill rest width
		// div to hold all video players of fetched videos
			// 20 videos per page in grid
		// buttons to navigate pages if more than 20 videos
	return (
		<div className="flex min-h-screen bg-gray-50">
			<Sidebar />

			<div className="flex flex-col flex-1 bg-gray-100">
				<header className="w-full px-8 py-4 border-b border-gray-300 bg-white shadow-sm">
					<h1 className="text-3xl font-semibold text-gray-800">Saved Videos</h1>
				</header>
			
				<div className="flex flex-col flex-1 items-center p-8 overflow-y-auto">
					<div className="bg-gray-800 p-6 rounded-3xl shadow-lg grid grid-cols-4 gap-6 max-h-[85vh] overflow-y-auto">
						{visibleVideos.length === 0 ? (
							<p className="text-gray-300">No videos found.</p>
						) : (
							visibleVideos.map((file, i) => (
								<div
									key={i}
									className="bg-black rounded-xl overflow-hidden relative hover:scale-[1.02] transition-transform duration-200"
								>
									<video
										className="w-full h-40 object-cover"
										controls
										preload="metadata"
										src={`/videos/${file}`}
									/>
									<div className="absolute bottom-0 left-0 w-full bg-black/50 text-white text-sm px-2 py-1 truncate">
										{file}
									</div>
								</div>
							))
						)}
					</div>

					<div className="flex items-center gap-4 mt-6">
						<button
							onClick={goPrev}
							disabled={page === 0}
							className={`px-4 py-2 rounded-md text-white font-medium ${
								page === 0
								? "bg-gray-500 cursor-not-allowed"
								: "bg-blue-500 hover:bg-blue-600"
							} transition`}
						>
							Previous
						</button>

						<span className="text-gray-700">
							Page {page + 1} of {totalPages}
						</span>

						<button
							onClick={goNext}
							disabled={page >= totalPages - 1}
							className={`px-4 py-2 rounded-md text-white font-medium ${
								page >= totalPages - 1
								? "bg-gray-500 cursor-not-allowed"
								: "bg-blue-500 hover:bg-blue-600"
							} transition`}
						>
							Next
						</button>
					</div>
				</div>
			</div>
		</div>
	);
}