"use client";
import Image from "next/image";
import { useEffect } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";


// Functionality:
// Check if logged in on load, if yes push to homepage
// On button login click, check if username and password match env variables
// set local storage item loggedIn to true and push to homepage
export default function LoginPage() {
	const router = useRouter();
	useEffect(() => {
		const isLoggedIn = sessionStorage.getItem("loggedIn");
		if (isLoggedIn) {
			router.push("/live");
		}
	}, []);

	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const handleLogin = (e: React.FormEvent) => {
		e.preventDefault();
		if (username.trim() === process.env.NEXT_PUBLIC_LOGIN_USER && password.trim() === process.env.NEXT_PUBLIC_LOGIN_PASS) {
			sessionStorage.setItem("loggedIn", "true");
			router.push("/homepage");
		} else {
			alert("Invalid credentials");
		}
	};


	// Structure
	// Full Screen, centered items, Background color #FF5A5F
		// rounded white box, padding 10, width 400px
			// image
			// form
				// label
				// input
				// label
				// input
				// button
	return (
		<div className="flex items-center justify-center min-h-screen bg-[#FF5A5F]">
			<div className="bg-white p-10 rounded-2xl shadow-xl w-[400px] text-center">
				<div className="flex flex-col items-center mb-8">
					<Image
						src="/guard_car_logo.png"
						alt="Logo"
						width={400}
						height={400}
						className="mb-2"
					/>
				</div>
				<form onSubmit={handleLogin} className="flex flex-col gap-4 text-left">
					<div>
						<label className="block text-sm font-semibold mb-1">
							Username
						</label>
						<input
							type="text"
							placeholder="Type your username"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#FF5A5F]"
						/>
					</div>
					<div>
						<label className="block text-sm font-semibold mb-1">
							Password
						</label>
						<input
							type="password"
							placeholder="Type your password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#FF5A5F]"
						/> 
					</div>
					<button type="submit" className="mt-4 bg-[#FF5A5F] text-white py-2 rounded-full font-semibold hover:bg-[#ff4449] transition">
						Sign in
					</button>
				</form>
			</div>
		</div>
	);
}