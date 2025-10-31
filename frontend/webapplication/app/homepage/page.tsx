"use client";
import Sidebar from "../components/sidebar";
import { useEffect } from "react";
import { useRouter } from "next/navigation";


// Functionality:
// Check if logged in on load, if no push to login
// sidebar and static content
export default function Homepage() {

    const router = useRouter();
        useEffect(() => {
            const isLoggedIn = sessionStorage.getItem("loggedIn");
            if (!isLoggedIn) {
                router.push("/");
            }
        }, []);

    
    // Structure:
	// left side nav bar
    // main content area
        // centered section with title and subtitle
        // section with 4 feature boxes in grid
            // each box with title and description
    return (
        <div className="flex min-h-screen bg-gray-50">
            <Sidebar />

            <main className="flex-1 flex flex-col items-center py-12 px-6">
                <section className="text-center max-w-2xl mb-12">
                    <h1 className="text-4xl font-extrabold mb-3 text-gray-900">
                        AI-Powered Vehicle Protection
                    </h1>
                    <p className="text-gray-600 text-lg mb-6">
                        GuardCar keeps watch 24/7 with intelligent surveillance, real-time alerts, and secure monitoring.
                    </p>
                </section>

                <section className="w-full max-w-3xl mb-12">
                    <h2 className="text-2xl font-bold mb-6 text-center">
                        Why GuardCar?
                    </h2>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition">
                            <h3 className="font-semibold mb-2">
                                24/7 Monitoring
                            </h3>
                            <p className="text-sm text-gray-600">
                                Always keep an eye on your vehicle, no matter where you are.
                            </p>
                        </div>
                        
                        <div className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition">
                            <h3 className="font-semibold mb-2">
                                AI Detection
                            </h3>
                            <p className="text-sm text-gray-600">
                                Smart tracking and suspicious activity alerts in real time.
                            </p>
                        </div>

                        <div className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition">
                            <h3 className="font-semibold mb-2">
                                Instant Notifications
                            </h3>
                            <p className="text-sm text-gray-600">
                                Receive SMS & email alerts the moment something happens.
                            </p>
                        </div>

                        <div className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition">
                            <h3 className="font-semibold mb-2">
                                Secure Cloud Storage
                            </h3>
                            <p className="text-sm text-gray-600">
                                Access past events anytime with video history.
                            </p>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
