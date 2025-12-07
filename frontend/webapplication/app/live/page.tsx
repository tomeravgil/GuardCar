"use client";
import { useEffect, useRef, useState } from "react";
import Sidebar from "../components/sidebar";
import { useRouter } from "next/navigation";

export default function LivePage() {
    const router = useRouter();

    // Login Check
    useEffect(() => {
        const isLoggedIn = sessionStorage.getItem("loggedIn");
        if (!isLoggedIn) router.push("/");
    }, [router]);

    // =============================================================
    // WEBSOCKET STREAM HANDLING
    // =============================================================
    const wsRef = useRef<WebSocket | null>(null);

    const imgMainRef = useRef<HTMLImageElement>(null);
    const imgCam0Ref = useRef<HTMLImageElement>(null);
    const imgCam1Ref = useRef<HTMLImageElement>(null);
    const [suspicionScore, setSuspicionScore] = useState<number>(0);

    // 0 = cam0, 1 = cam1, 2 = both
    const [viewMode, setViewMode] = useState<0 | 1 | 2>(0);
    const [recordingStatus, setRecordingStatus] = useState<boolean>(false);
    const viewModeRef = useRef(0);

    const changeView = (mode) => {
        viewModeRef.current = mode;
        setViewMode(mode);
        console.log("Changing view to mode:", mode);
        wsRef.current?.send(JSON.stringify({ camera: mode }));
    };

    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/video");
        ws.binaryType = "arraybuffer";
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WS connected.");
            ws.send(JSON.stringify({ camera: 0 }));
        };

        ws.onmessage = (event) => {

            const bytes = new Uint8Array(event.data);
            const url = URL.createObjectURL(new Blob([bytes], { type: "image/jpeg" }));
            imgMainRef.current!.src = url;
            return;
        };

        return () => ws.close();
    }, []);   // IMPORTANT: only once

    // =============================================================
    // SSE HANDLING
    // =============================================================
    useEffect(() => {
        console.log("Connecting to SSE server...");

        const sse = new EventSource("http://127.0.0.1:8000/api/sse");

        sse.addEventListener("open", () => {
            console.log("SSE connected.");
        });

        // Example: Suspicion Detected (you have this event type)
        sse.addEventListener("suspicion", (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.suspicion_score !== undefined) {
                    if (data.suspicion_score !== suspicionScore){
                        setSuspicionScore(data.suspicion_score.toFixed(2));
                    }
                }
            } catch (err) {
                console.warn("Invalid SSE JSON:", err);
            }
        });

        // Example: Recording Status
        sse.addEventListener("recording", (event) => {
            const data = JSON.parse(event.data);
            console.log("Recording Status:", data);
            if (data.recording !== undefined) {
                if (data.recording !== recordingStatus) {
                    setRecordingStatus(data.recording);
                }
            }
        });


        return () => {
            console.log("Closing SSE.");
            sse.close();
        };
    }, []);


    // Recent videos
    const [recentVideos, setRecentVideos] = useState<string[]>([]);
    useEffect(() => {
        const loadVideos = async () => {
            try {
                const res = await fetch("/api/videos");
                const data = await res.json();
                const sorted = data.sort().reverse();
                setRecentVideos(sorted.slice(0, 5));
            } catch (err) {
                console.error("Error loading videos:", err);
            }
        };
        loadVideos();
    }, []);

    return (
        <div className="flex min-w-screen bg-gray-50">
            <Sidebar />

            <div className="flex flex-col flex-1 bg-gray-100">
                {/* Header */}
                <header className="w-full px-8 py-4 border-b border-gray-300 bg-white shadow-sm flex justify-between">
                    <div>
                        <h1 className="text-3xl font-semibold text-gray-800">Live View</h1>
                        <div>
                            <p className="text-gray-600 mt-1">Suspicion Score: <span className="font-bold">{suspicionScore}</span></p>
                            <p className="">
                            Recording Status:{" "}
                            <span className="font-bold flex items-center gap-2">
                                {recordingStatus ? (
                                <span className="relative flex items-center justify-center">
                                    {/* Outer black circle */}
                                    <span className="w-4 h-4 bg-black rounded-full flex items-center justify-center">
                                    {/* Inner glowing red circle */}
                                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_10px_3px_rgba(255,0,0,0.8)]"></span>
                                    </span>
                                </span>
                                ) : (
                                <span className="text-gray-500">Not Recording</span>
                                )}
                            </span>
                            </p>
                        </div>
                    </div>
                    


                    <div className="flex gap-3">
                        <button
                            onClick={() => changeView(0)}
                            className={`px-4 py-2 rounded-lg font-semibold ${
                                viewMode === 0 ? "bg-[#FF5A5F] text-white" : "bg-white text-black border"
                            }`}
                        >
                            Camera 1
                        </button>

                        <button
                            onClick={() => changeView(1)}
                            className={`px-4 py-2 rounded-lg font-semibold ${
                                viewMode === 1 ? "bg-[#FF5A5F] text-white" : "bg-white text-black border"
                            }`}
                        >
                            Camera 2
                        </button>

                        <button
                            onClick={() => changeView(2)}
                            className={`px-4 py-2 rounded-lg font-semibold ${
                                viewMode === 2 ? "bg-[#FF5A5F] text-white" : "bg-white text-black border"
                            }`}
                        >
                            Both
                        </button>
                    </div>
                </header>

                {/* Live Video View */}
                <div className="flex flex-col items-center justify-start flex-1 bg-gray-100 py-10">

                    {/* MAIN STREAM AREA */}
                    <div className="relative w-full max-w-[1200px] aspect-video bg-black rounded-2xl overflow-hidden shadow-lg flex items-center justify-center">
                        <img ref={imgMainRef} className="w-full h-full object-cover rounded-2xl" alt="Live Camera" />
                    </div>
                    {/* Recent Videos */}
                    <h2 className="text-2xl font-semibold mt-10 mb-4">Most Recent Videos</h2>

                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 w-full max-w-[1200px]">
                        {recentVideos.length === 0 ? (
                            <p className="text-gray-600 col-span-full text-center">No videos found.</p>
                        ) : (
                            recentVideos.map((file) => (
                                <div key={file} className="cursor-pointer flex flex-col items-center group">
                                    <video
                                        src={`/videos/${encodeURIComponent(file)}`}
                                        className="rounded-lg shadow-md border border-gray-300 w-[160px] h-[90px] object-cover"
                                        controls
                                        muted
                                        preload="metadata"
                                        playsInline
                                        controlsList="nodownload"
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
