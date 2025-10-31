"use client";
import { useState } from "react";
import Sidebar from "../components/sidebar";

export default function SettingsPage() {


	const [formData, setFormData] = useState({
		user: "admin",
		password: "1234",
		email: "blank@gmail.com",
		phone: "555-555-5555",
		server: "192.168.1.190",
		scores: { person: "", dog: "", car: "" },
	});


	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;
		
		if (name.startsWith("scores.")) {
			const key = name.split(".")[1];
			setFormData((prev) => ({
				...prev,
				scores: { ...prev.scores, [key]: value },
			}));
		}
		else {
			setFormData((prev) => ({ ...prev, [name]: value }));
		}
	};


	// To Connect to backend API
	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		
		try {
			
			
			// if (!request.ok){
			// 	throw new Error("Request failed");
			// }
			// else {
			// 	alert("Settings saved!");
			// }
		
		} catch {
			alert("Error saving settings.");
		}
	};

	return (
		<div className="flex min-h-screen bg-gray-50">
			<Sidebar />
			<main className="flex-1 p-10">
				<h1 className="text-3xl font-bold text-gray-800 mb-8">Settings</h1>

				<form
					onSubmit={handleSubmit}
					className="bg-white p-8 rounded-2xl shadow-md space-y-6 w-full"
				>
					{[
						{ label: "User", name: "user", type: "text" },
						{ label: "Password", name: "password", type: "password" },
						{ label: "Email", name: "email", type: "email" },
						{ label: "Phone", name: "phone", type: "tel" },
						{ label: "Server Address", name: "server", type: "text" },
					].map((input) => (
						<div key={input.name}>
							<label className="block text-sm font-semibold mb-1">
								{input.label}
							</label>
							<input
								type={input.type}
								name={input.name}
								value={(formData as any)[input.name]}
								onChange={handleChange}
								placeholder={`Enter ${input.label.toLowerCase()}`}
								className="w-full border border-gray-300 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#FF5A5F]"
							/>
						</div>
					))}

					<div className="mt-8">
						<h2 className="text-xl font-semibold mb-4 text-gray-700">
							Suspicion Scores
						</h2>
						<div className="pl-4 border-l-2 border-gray-200 space-y-4">
							{[
								{ label: "Person", name: "scores.person" },
								{ label: "Bike", name: "scores.bike" },
								{ label: "Car", name: "scores.car" },
								{ label: "Motorcycle", name: "scores.motorcyle" },
								{ label: "Bus", name: "scores.bus" },
								{ label: "Truck", name: "scores.truck" },
							].map((input) => (
								<div key={input.name}>
									<label className="block text-sm font-semibold mb-1">
										{input.label}
									</label>
									<input
										type="number"
										name={input.name}
										value={
										(formData.scores as any)[input.name.split(".")[1]] || ""
										}
										onChange={handleChange}
										placeholder={`Enter ${input.label.toLowerCase()}`}
										className="w-full border border-gray-300 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#FF5A5F]"
									/>
								</div>
							))}
						</div>
					</div>

					<div className="flex justify-end">
						<button
							type="submit"
							className="bg-[#FF5A5F] text-white px-8 py-3 rounded-full font-semibold hover:bg-[#ff4449] transition"
						>
							Save
						</button>
					</div>
				</form>
			</main>
		</div>
	);
}
