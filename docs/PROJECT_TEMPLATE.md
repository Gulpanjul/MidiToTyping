# Project Template & Setup Instructions

Template lengkap untuk membuat project baru dengan standar clean code fe-acara.

## 📋 Quick Start Command

Gunakan prompt ini untuk membuat project baru dengan Claude Code:

```
Buat project Next.js baru bernama [PROJECT_NAME] dengan standar clean code dan architektur yang sama seperti fe-acara. 

Referensi: Lihat CLAUDE.md untuk dokumentasi lengkap standar yang harus diterapkan.

Persyaratan:
- Setup folder structure sesuai CLAUDE.md (components/commons, layouts, ui, views)
- Konfigurasi TypeScript strict mode dengan path alias @/*
- Setup TailwindCSS dengan prettier-plugin-tailwindcss
- Setup Prettier & ESLint (next/core-web-vitals)
- Setup Git hooks dengan husky & commitlint
- Install dependencies: Next.js 15, React 19, TailwindCSS, HeroUI, React Query, Axios, NextAuth, React Hook Form, Yup
- Setup .env.example dengan required environment variables
- Buat README.md dengan dokumentasi project
- Setup axios instance di libs/axios/instance.ts
- Buat endpoint.constant.ts di services/
- Buat contoh service, type, component, dan hook sesuai pattern di CLAUDE.md

Ikuti semua standar di CLAUDE.md untuk:
- Component architecture & naming
- Services & API layer
- Custom hooks pattern
- Types & interfaces
- Utilities & helpers
- Constants management
- Styling dengan Tailwind
- Code quality
- Git & commit standards
```

## 🏗️ Folder Structure Template

Struktur folder yang harus dibuat untuk project baru:

```
[PROJECT_NAME]/
├── .git/
├── .husky/
│   ├── pre-commit
│   └── commit-msg
├── node_modules/
├── public/
│   └── images/
│       └── general/
│           └── logo.svg
├── src/
│   ├── components/
│   │   ├── commons/
│   │   │   ├── Component1/
│   │   │   │   ├── Component1.tsx
│   │   │   │   └── index.tsx
│   │   │   └── Component2/
│   │   ├── layouts/
│   │   │   ├── MainLayout/
│   │   │   │   ├── MainLayout.tsx
│   │   │   │   ├── MainLayout.constants.tsx
│   │   │   │   └── index.tsx
│   │   │   └── AuthLayout/
│   │   ├── ui/
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   └── Modal/
│   │   └── views/
│   │       └── Feature/
│   │           ├── Feature.tsx
│   │           ├── Feature.constants.tsx
│   │           ├── useFeature.ts
│   │           └── SubFeature/
│   ├── config/
│   │   └── environment.ts
│   ├── libs/
│   │   └── axios/
│   │       ├── instance.ts
│   │       └── responseHandler.ts
│   ├── services/
│   │   ├── endpoint.constant.ts
│   │   ├── feature1.service.ts
│   │   └── feature2.service.ts
│   ├── types/
│   │   ├── Feature1.d.ts
│   │   └── Feature2.d.ts
│   ├── utils/
│   │   ├── cn.ts
│   │   ├── currency.ts
│   │   └── date.ts
│   ├── hooks/
│   │   └── useCustom.ts
│   ├── constants/
│   │   └── app.constants.ts
│   └── pages/
│       ├── index.tsx
│       ├── about.tsx
│       ├── api/
│       │   └── hello.ts
│       └── [...slug].tsx
├── .env.example
├── .eslintrc.json
├── .gitignore
├── .prettierrc
├── commitlint.config.js
├── next.config.mjs
├── postcss.config.mjs
├── package.json
├── package-lock.json
├── tsconfig.json
├── README.md
├── CLAUDE.md
└── PROJECT_TEMPLATE.md
```

## 📦 Package.json Template

```json
{
  "name": "[project-name]",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@heroui/react": "^2.6.14",
    "@hookform/resolvers": "^3.9.0",
    "@tanstack/react-query": "^5.62.8",
    "axios": "^1.7.2",
    "clsx": "^2.1.1",
    "framer-motion": "^11.3.8",
    "next": "^15.1.1",
    "next-auth": "^4.24.11",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-hook-form": "^7.52.1",
    "react-icons": "^5.2.1",
    "tailwind-merge": "^2.4.0",
    "yup": "^1.4.0"
  },
  "devDependencies": {
    "@commitlint/cli": "^19.6.0",
    "@commitlint/config-conventional": "^19.6.0",
    "@types/node": "^20",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint": "^9.16.0",
    "eslint-config-next": "^15.1.1",
    "husky": "^9.1.7",
    "postcss": "^8",
    "prettier": "^3.3.3",
    "prettier-plugin-tailwindcss": "^0.6.5",
    "tailwindcss": "^3.4.1",
    "typescript": "^5"
  }
}
```

## 🔧 Configuration Files

### .eslintrc.json
```json
{
  "extends": "next/core-web-vitals",
  "rules": {
    "react-hooks/exhaustive-deps": "off"
  }
}
```

### .prettierrc
```json
{
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

### tsconfig.json
```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "target": "ES2022"
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### postcss.config.mjs
```js
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};

export default config;
```

### commitlint.config.js
```js
module.exports = {
  extends: ["@commitlint/config-conventional"],
};
```

### next.config.mjs
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.example.com",
      },
    ],
  },
};

export default nextConfig;
```

## 📝 Initial Files to Create

### 1. config/environment.ts
```typescript
const environment = {
  API_URL: process.env.NEXT_PUBLIC_API_URL,
  AUTH_SECRET: process.env.NEXTAUTH_SECRET,
  // Tambahkan env vars lain sesuai kebutuhan
};

export default environment;
```

### 2. libs/axios/instance.ts
```typescript
import environment from "@/config/environment";
import { SessionExtended } from "@/types/Auth";
import axios from "axios";
import { getSession } from "next-auth/react";

const headers = {
  "Content-Type": "application/json",
};

const instance = axios.create({
  baseURL: environment.API_URL,
  headers,
  timeout: 60 * 1000,
});

// Request interceptor - ambil token dari NextAuth session
instance.interceptors.request.use(
  async (request) => {
    const session: SessionExtended | null = await getSession();
    if (session && session.accessToken) {
      request.headers.Authorization = `Bearer ${session.accessToken}`;
    }
    return request;
  },
  (error) => Promise.reject(error),
);

// Response interceptor
instance.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);

export default instance;
```

### 3. libs/axios/responseHandler.ts
```typescript
import { AxiosError } from "axios";
import { signOut } from "next-auth/react";

interface ErrorResponseData {
  data: {
    name: string;
  };
}

const onErrorHandler = (error: Error) => {
  const { response } = error as AxiosError;
  const res = response?.data as ErrorResponseData;
  if (response && res?.data?.name === "TokenExpiredError") {
    signOut();
  }
};

export { onErrorHandler };
```

### 4. services/endpoint.constant.ts
```typescript
const endpoint = {
  AUTH: "/auth",
  BANNER: "/banners",
  CATEGORY: "/category",
  EVENT: "/events",
  MEDIA: "/media",
  ORDER: "/orders",
  REGION: "/regions",
  TICKET: "/tickets",
};

export default endpoint;
```

### 5. utils/cn.ts
```typescript
import { ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 6. types/Example.d.ts
```typescript
interface IExample {
  _id?: string;
  name?: string;
  description?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export type { IExample };
```

### 7. .env.example
```
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXTAUTH_SECRET=your_secret_key_here
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_MIDTRANS_SNAP_URL=https://app.sandbox.midtrans.com/snap/snap.js
NEXT_PUBLIC_MIDTRANS_CLIENT_KEY=your_midtrans_client_key
```

## 🚀 Setup Steps

1. **Initialize Project**
   ```bash
   npx create-next-app@latest [project-name] --typescript --tailwind
   cd [project-name]
   ```

2. **Create Folder Structure**
   - Create all folders according to template above

3. **Install Additional Dependencies**
   ```bash
   npm install @heroui/react @tanstack/react-query axios next-auth react-hook-form yup @hookform/resolvers
   npm install -D @commitlint/cli @commitlint/config-conventional husky
   ```

4. **Setup Git & Husky**
   ```bash
   git init
   npx husky install
   npx husky add .husky/pre-commit "npm run lint"
   npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
   ```

5. **Copy Configuration Files**
   - Copy all config files from section above (.eslintrc.json, .prettierrc, etc.)

6. **Create Initial Files**
   - Create files in libs, services, utils, types as shown above

7. **Setup Environment Variables**
   - Copy .env.example to .env.local and fill in values

8. **Create README**
   - Document your project features, setup, and usage

9. **Initialize Git Repository**
   ```bash
   git add .
   git commit -m "feat: initial project setup"
   git branch -M main
   git remote add origin [repository-url]
   ```

## ✅ Verification Checklist

Before considering project ready:

- [ ] TypeScript compiles without errors
- [ ] ESLint passes: `npm run lint`
- [ ] Folder structure matches template
- [ ] .env.example has all required variables
- [ ] README.md is complete and accurate
- [ ] Example component created following patterns
- [ ] Example service created following patterns
- [ ] Example hook created following patterns
- [ ] Example type definition created
- [ ] Prettier formats code correctly
- [ ] Git hooks working (pre-commit, commit-msg)
- [ ] Initial commit uses conventional format
- [ ] Remote repository configured

## 📚 Next Steps After Setup

1. **Create Page Layouts**
   - Implement main layout components

2. **Setup Authentication**
   - Configure NextAuth or alternative auth solution
   - Create login/register pages

3. **API Integration**
   - Create service files for each API resource
   - Create custom hooks for data fetching

4. **Component Library**
   - Build reusable UI components in components/ui
   - Create common components in components/commons

5. **Pages & Views**
   - Create page-specific views
   - Integrate components into pages

6. **Testing**
   - Setup testing framework
   - Write tests for critical functions

7. **Deployment**
   - Configure CI/CD pipeline
   - Deploy to hosting platform

---

**Template Version**: 1.0.0
**Last Updated**: 2026-04-13
