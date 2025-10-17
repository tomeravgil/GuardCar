"use client";
import Image from "next/image";
import { useState } from "react";
import { useRouter } from "next/navigation";


export default function LoginPage() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const router = useRouter();

	const handleLogin = (e: React.FormEvent) => {
		e.preventDefault();

		if (username === process.env.NEXT_PUBLIC_LOGIN_USER && password === process.env.NEXT_PUBLIC_LOGIN_PASS) {
		localStorage.setItem("loggedIn", "true");
		router.push("/");
	} else {
		alert("Invalid credentials");
	}
};

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
			<label className="block text-sm font-semibold mb-1">Username</label>
			<input
				type="text"
				placeholder="Type your username"
				value={username}
				onChange={(e) => setUsername(e.target.value)}
				className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#FF5A5F]"
			/>
		</div>
		<div>
			<label className="block text-sm font-semibold mb-1">Password</label>
			<input
				type="password"
				placeholder="Type your password"
				value={password}
				onChange={(e) => setPassword(e.target.value)}
				className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#FF5A5F]"
			/>
		</div>
		<button
			type="submit"
			className="mt-4 bg-[#FF5A5F] text-white py-2 rounded-full font-semibold hover:bg-[#ff4449] transition"
		>
			
			Sign in
		</button>
		</form>
	</div>
	</div>
);
}