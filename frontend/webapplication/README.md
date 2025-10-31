
# Web App information

Brief reference for the frontend Next.js application in this repository.

## Quick summary
- Framework: Next.js - Next v15.5.4
- React: 19.1.0
- Language: TypeScript
- Node: v22.20.0
- Styling: Tailwind CSS
- Linting: ESLint configured (see `eslint.config.mjs`)

This file gives a short setup + run guide, a small file map (where to find the layout/pages), the intended frontend tasks, and acceptance criteria.

## Install & run (developer flow)
Open a Comand Promt terminal in `frontend/webapp` then:

```powershell
# install dependencies (npm is the default here)
npm install

# run the dev server (hot reload on change)
npm run dev
```

Notes:
- The project `package.json` includes `dev`/`build`/`start` scripts and uses Next's turbopack flag in dev/build. If your environment doesn't support turbopack, remove `--turbopack` from the scripts in `package.json`.
- You can also use `pnpm` or `yarn` if you prefer; the README in this repo shows the standard Next.js commands.

Default port: http://localhost:3000

## Intended frontend tasks & scope
The frontend was scoped with these goals (developer checklist):

- Scaffold a fresh Next.js app (TypeScript + App Router)
- Implement a global layout (Shell) that matches the wireframes
- Add placeholder pages/sections to demonstrate routing and layout reuse
- Provide a minimal design system using Tailwind (colors, spacing, typography)
- Create mobile and desktop designs for each core page (in `frontend/Designs`)
- Add linting (ESLint) and formatting defaults

## To Do
- clean up all pages
### live page
- add real source
### settings
- connect to api
