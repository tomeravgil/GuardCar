import fs from "fs";
import path from "path";
import { NextResponse } from "next/server";

export async function GET() {
  	const dirPath = path.join(process.cwd(), "public/videos");
  	let files: string[] = [];

	try {
		files = fs.readdirSync(dirPath).filter((f) => f.endsWith(".mp4"));
	} catch (err) {
		console.error("Error reading videos folder:", err);
	}

  	return NextResponse.json(files);
}