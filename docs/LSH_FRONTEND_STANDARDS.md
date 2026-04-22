# FE-Acara Clean Code Standards & Project Guidelines

Dokumen ini mendefinisikan standar clean code, architectural patterns, dan best practices untuk semua project frontend yang mengikuti struktur serupa dengan `fe-acara`.

Standar ini mengacu pada kebijakan resmi **LSH Group IT Department**:
- **AI-Assisted Development Standards** (v1.0, 31 March 2026) — Issued by Afif Kamal Fiska, Regional IT Manager
- **AI Development Discipline Framework** (v1.0, 31 March 2026) — 4D Protocol & 6-Gate Protocol

---

## 🏢 LSH Group IT Standards Integration

### File Header Block (Wajib untuk setiap file baru)

Setiap script atau config file **harus** dimulai dengan header block standar:

```tsx
// ============================================================
// File: [filename]
// Date: [YYYY-MM-DD]
// Author: [Your name and role]
// Task: [Brief description of what this file does]
// AI-Assisted: [Yes/No — if Yes, which tool was used]
// ============================================================
```

### File Naming Convention

**Pattern**: `YYYY-MM-DD_{document-type}_{brief-description}.{ext}`

**Rules**:
- Date prefix selalu menggunakan format `YYYY-MM-DD`
- Document type dan description menggunakan **lowercase kebab-case**
- Extension harus sesuai dengan jenis file sebenarnya
- Jangan overwrite file yang sudah ada — gunakan `_v2`, `_v3` jika perlu

**Contoh**:
```
2026-04-13_rfc_deploy-payment-gateway.md
2026-04-13_deploy-script_patch-auth-module.sh
2026-04-13_firewall-rules_block-external-rdp.conf
```

> **Catatan**: Konvensi ini berlaku untuk dokumen, script deployment, dan konfigurasi. Untuk source code React/Next.js, gunakan konvensi PascalCase/camelCase sesuai section di bawah.

### Security Standards (Wajib)

#### Aturan Keamanan Utama
1. **No real secrets in code** — JANGAN hardcode API keys, passwords, connection strings, atau tokens. Gunakan placeholder: `<REPLACE_WITH_API_KEY>`, `<REPLACE_WITH_PASSWORD>`
2. **No PII in examples** — Gunakan data sintetis (John Doe, 192.168.x.x, example.com)
3. **Error handling wajib** — Semua script harus include error checking dan graceful failure
4. **Rollback-ready** — Setiap deployment/perubahan infrastruktur harus punya rollback procedure
5. **Validated** — Include pre-execution checks (dry-run, syntax validation) dimana memungkinkan

#### Jangan Pernah Generate Script yang:
- Download dan pipe ke shell (`curl | bash`)
- Mengandung hardcoded real credentials
- Disable security features tanpa justifikasi terdokumentasi
- Mengandung `permit any any` tanpa explicit deny rule

### AI Transparency (Wajib)

Saat sharing work yang AI-assisted, sertakan transparency note:

**Untuk penggunaan internal tim:**
```
Produced with AI assistance | Reviewed by: [Your Name]
```

**Untuk management atau sharing external:**
```
AI Role: [Drafted / Co-authored / Automated]
Human verification: [Reviewed / Tested / Approved]
```

**Definisi AI Role:**
| Label | Meaning |
|-------|---------|
| **Drafted** | AI memproduksi konten awal; manusia review dan approve |
| **Co-authored** | Manusia dan AI iterasi bersama (collab mode) |
| **Automated** | AI mengeksekusi task rutin yang terdefinisi dengan baik |

### Sensitivity Classification

| Level | Label | Contoh |
|-------|-------|--------|
| 0 | PUBLIC | KB articles, user guides, dokumentasi umum |
| 1 | INTERNAL | Sprint plans, status reports, meeting notes |
| 2 | CONFIDENTIAL | Risk assessments, audit reports, RFCs, policies |
| 3 | RESTRICTED | Pen test results, incident reports, firewall rules, IAM configs |

---

## 🔄 4D Protocol — Working with AI Effectively

> Berdasarkan: Framework for AI Fluency v1.1 (Dakan & Feller, 2025)

### D1: Delegation — "Right task, right mode, right tool"

**Tiga Mode Bekerja:**
| Mode | Artinya | Kapan Digunakan |
|------|---------|-----------------|
| **Auto** | AI eksekusi independen, Anda review hasilnya | Task rutin, scope jelas, boilerplate |
| **Collab** | AI draft, Anda review di checkpoint, iterasi bersama | Strategic work, complex tasks, architecture |
| **Setup** | AI build sesuatu yang berjalan independen | Automation scripts, bots, scheduled systems |

**Default Rules of Thumb:**
- High-impact tasks → **collab**
- Routine scripts, configs, documentation → **auto**
- Policy, architecture, presentations → **collab**
- Building bots, hooks, automation → **setup**

### D2: Description — "Understand intent, not just instruction"

- Berikan **context**, bukan hanya perintah
- Berikan **what** dan **why**; biarkan AI tentukan **how**
- Untuk task rutin — cukup instruksi langsung
- Untuk task strategis — investasikan 30 detik mendefinisikan "success looks like what?"

### D3: Discernment — "Surface problems, don't hide them"

Setelah menghasilkan work yang signifikan, jujur assess:

```
Confidence: [HIGH / MEDIUM / LOW]
What I'm sure about: [key strengths]
What I'm uncertain about: [assumptions, gaps, risks]
What this doesn't cover: [known limitations]
```

- **"I don't know"** selalu acceptable. **Guessing is not** — terutama untuk security, infrastructure, dan database.
- Jika AI memberi sesuatu yang uncertain, **minta penjelasan** sebelum digunakan.
- **Flag it, don't hide it** — jika deliverable punya known limitations, nyatakan di awal.

### D4: Diligence — "Own what you produce"

- **Anda selalu accountable**. Jika deliverable ada nama Anda, Anda yang bertanggung jawab.
- **Review sebelum share** — "Have I verified the key facts? Am I comfortable vouching for this?"
- **Jangan claim yang belum selesai** — partial work harus dilabel sebagai partial.
- **Fact-check** — terutama statistik, tanggal, dan spesifikasi teknis (AI bisa halusinasi).

---

## 🚦 6-Gate Protocol — Quality Checkpoints

### Gate 1: Security Review — "Untrusted until proven safe"

Review terhadap **OWASP Top 10**:
- Broken access control
- Injection vulnerabilities (SQL, command, XSS)
- Security misconfiguration (open defaults, unnecessary features)
- Hardcoded secrets atau insecure defaults

**Rule**: No AI-generated code yang menyentuh auth, security, atau infrastructure boleh live tanpa **manual security review**.

### Gate 2: Comprehension — "Never deliver what you can't explain"

Sebelum menerima AI-generated code, pastikan bisa jawab:
- Apa yang dilakukan code ini, step by step?
- Asumsi apa yang dibuat?
- Apa yang break jika input tidak sesuai?

**Rule**: Jika tidak bisa jelaskan ke kolega, jangan ship.

### Gate 3: Technical Debt — "Integrate, don't accumulate"

- Sebelum membuat script/config baru, **cek apakah yang serupa sudah ada**
- Jika ada file serupa, **update** daripada membuat duplikat
- Write tests **alongside features**, bukan afterthought

**Rule**: Search before you create. Update before you duplicate.

### Gate 4: Perception Honesty — "Measure reality, not feeling"

- Set **context budget** — jika task lebih banyak back-and-forth daripada menulis sendiri, tulis sendiri
- Track ketika AI membuat jenis mistake yang sama berulang — ubah approach
- **Measure actual delivery time**, bukan perceived time

**Rule**: AI harus save time secara net. Jika tidak, ubah approach.

### Gate 5: Scope Control — "Constrain the blast radius"

- **Jangan pernah** arahkan AI tools ke production dengan write access
- **Definisikan boundary** sebelum mulai: file/folder mana yang boleh disentuh
- Action yang modify/delete file harus **require explicit confirmation**

**Rule**: Define the boundary before you start. If AI wants to go outside it, stop and review.

### Gate 6: Risk-Tiered Review — "Not all output deserves the same trust"

| Deliverable Type | Review Tier | What To Do |
|-----------------|-------------|------------|
| Documentation, KB articles, reports | Tier 1 — Light | Quick read, check facts, deliver |
| Business logic, application code, pipelines | Tier 2 — Careful | Read thoroughly, check assumptions, include tests |
| Auth, security, crypto, IAM configs | Tier 3 — Manual | Review line by line. Never auto-accept. |
| DB schema, migrations, data changes | Tier 4 — High-risk | Test in staging. Include rollback. Dry-run first. |
| Infrastructure config, firewall rules, IaC | Tier 5 — Line-by-line | Walk through every line. Include rollback. |

**Rule**: Match your review effort to the risk level of what you're producing.

---

## 🧭 Quick Reference Cards

### The 4Ds
| D | Principle | One-liner |
|---|-----------|-----------|
| D1 | Delegation | Right task, right mode, right tool |
| D2 | Description | Understand intent, not just instruction |
| D3 | Discernment | Surface problems, don't hide them |
| D4 | Diligence | Own what you produce |

### The 6 Gates
| Gate | Principle | One-liner |
|------|-----------|-----------|
| G1 | Security | Untrusted until proven safe |
| G2 | Comprehension | Never deliver what you can't explain |
| G3 | Technical Debt | Search before you create |
| G4 | Perception | Measure reality, not feeling |
| G5 | Scope | Define the boundary before you start |
| G6 | Risk Tier | Match review effort to risk level |

---

## 📋 Project Structure

```
src/
├── components/
│   ├── commons/         # Reusable components (AppShell, PageHead, etc.)
│   ├── layouts/         # Page layouts (AuthLayout, DashboardLayout, etc.)
│   ├── ui/              # UI components (Button, Card, Input, etc.)
│   └── views/           # Page-specific components (Admin views, user pages)
├── config/              # Environment configuration (environment.ts)
├── libs/
│   └── axios/           # HTTP client (instance.ts, responseHandler.ts)
├── services/            # API service layer (business logic, HTTP calls)
├── types/               # TypeScript type definitions (.d.ts)
├── utils/               # Utility functions (cn, currency, date formatting, etc.)
├── hooks/               # Global custom React hooks (useChangeUrl, useDebounce, etc.)
├── constants/           # Global constants (list.constants.ts)
└── pages/               # Next.js Pages Router directory
```

## 🎯 Key Standards

### 1. Component Architecture

#### General Rules
- **One component per file** (except index.tsx for exports)
- **Index file exports** - every component folder has `index.tsx` that re-exports the main component
- **Props interface** - use `interface PropTypes` for component props
- **Destructure props** - always destructure props in component signature
- **Use TypeScript** - strict mode enabled, all props must be typed

#### Component Template
```tsx
interface PropTypes {
  className?: string;
  title: string;
  isLoading?: boolean;
}

const MyComponent = (props: PropTypes) => {
  const { className, title, isLoading } = props;
  
  return (
    <div className={cn(className, "base-class")}>
      {/* Component JSX */}
    </div>
  );
};

export default MyComponent;
```

#### Index File Pattern
```tsx
// components/ui/MyComponent/index.tsx
import MyComponent from "./MyComponent";

export default MyComponent;
```

### 2. Component Organization

#### Commons Components
- **Purpose**: Reusable across multiple pages
- **Examples**: `AppShell`, `PageHead`, `DropdownAction`
- **Naming**: PascalCase

#### Layout Components
- **Purpose**: Page layout wrappers
- **Pattern**: Include `.constants.tsx` for layout-specific constants
- **Examples**: `AuthLayout`, `DashboardLayout`, `LandingPageLayout`
- **Structure**: Main component + sub-components + hooks

#### UI Components
- **Purpose**: Presentational, highly reusable components
- **Examples**: `CardEvent`, `DataTable`, `InputFile`, `Toaster`
- **Focus**: Props-driven, minimal internal logic

#### View Components
- **Purpose**: Page-specific, business logic-heavy components
- **Pattern**: 
  - Main component file (e.g., `Banner.tsx`)
  - Custom hook (e.g., `useBanner.ts`)
  - Constants file (e.g., `Banner.constants.tsx`)
  - Sub-components for modals/tabs (e.g., `AddBannerModal/`)
- **Examples**: Admin views, user profile pages

### 3. Custom Hooks Pattern

#### File Naming
- **Hook file**: `use{ComponentName}.ts` or `use{FeatureName}.ts`
- **Placement**: Same folder as component
- **Export**: From component folder's index.tsx if shared

#### Hook Template (View-level with React Query)
```tsx
// components/views/Example/useExample.ts
import useChangeUrl from "@/hooks/useChangeUrl";
import exampleServices from "@/services/example.service";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/router";
import { useState } from "react";

const useExample = () => {
  const [selectedId, setSelectedId] = useState<string>("");
  const router = useRouter();
  const { currentLimit, currentPage, currentSearch } = useChangeUrl();

  const getExamples = async () => {
    let params = `limit=${currentLimit}&page=${currentPage}`;
    if (currentSearch) {
      params += `&search=${currentSearch}`;
    }
    const res = await exampleServices.getExamples(params);
    const { data } = res;
    return data;
  };

  const {
    data: dataExamples,
    isLoading: isLoadingExamples,
    isRefetching: isRefetchingExamples,
    refetch: refetchExamples,
  } = useQuery({
    queryKey: ["Examples", currentPage, currentLimit, currentSearch],
    queryFn: () => getExamples(),
    enabled: router.isReady && !!currentPage && !!currentLimit,
  });

  return {
    dataExamples,
    isLoadingExamples,
    isRefetchingExamples,
    refetchExamples,
    selectedId,
    setSelectedId,
  };
};

export default useExample;
```

#### Global Hook Template (Reusable across views)
```tsx
// hooks/useDebounce.tsx
import { useRef } from "react";

const useDebounce = () => {
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const debounce = (func: Function, delay: number) => {
    if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    debounceTimeout.current = setTimeout(() => {
      func();
      debounceTimeout.current = null;
    }, delay);
  };

  return debounce;
};

export default useDebounce;
```

> **Catatan**: Global hooks di `src/hooks/` boleh menggunakan ekstensi `.tsx` karena bisa mengandung React types. View-level hooks biasanya `.ts`.

### 4. Config & Environment

#### Structure
- **Location**: `src/config/`
- **File**: `environment.ts`
- **Purpose**: Centralized environment variable access

#### Config Template
```tsx
// config/environment.ts
const environment = {
  API_URL: process.env.NEXT_PUBLIC_API_URL,
  AUTH_SECRET: process.env.NEXTAUTH_SECRET,
  MIDTRANS_SNAP_URL: process.env.NEXT_PUBLIC_MIDTRANS_SNAP_URL,
  MIDTRANS_CLIENT_KEY: process.env.NEXT_PUBLIC_MIDTRANS_CLIENT_KEY,
};

export default environment;
```

> **Catatan**: Jangan akses `process.env` langsung di component/service. Selalu gunakan `environment` object dari config. Ini mempermudah refactoring dan type checking.

### 5. Services & API Layer

#### Structure
- **File naming**: `{feature}.service.ts`
- **Export pattern**: Default export of object with methods
- **Method naming**: Verb + noun pattern (e.g., `getEvents`, `addEvent`, `updateEvent`)

#### Service Template
```tsx
// services/example.service.ts
import instance from "@/libs/axios/instance";
import endpoint from "./endpoint.constant";
import { IExample } from "@/types/Example";

const exampleServices = {
  getExamples: (params?: string) => 
    instance.get(`${endpoint.EXAMPLE}?${params}`),
  getExampleById: (id: string) => 
    instance.get(`${endpoint.EXAMPLE}/${id}`),
  addExample: (payload: IExample) => 
    instance.post(endpoint.EXAMPLE, payload),
  updateExample: (id: string, payload: IExample) => 
    instance.put(`${endpoint.EXAMPLE}/${id}`, payload),
  deleteExample: (id: string) => 
    instance.delete(`${endpoint.EXAMPLE}/${id}`),
};

export default exampleServices;
```

#### Endpoint Management
- **File**: `services/endpoint.constant.ts`
- **Pattern**: Centralized endpoint definitions
- **Usage**: Import and reference in all service files

### 6. Types & Interfaces

#### File Naming & Extension
- **Format**: `{Feature}.d.ts`
- **Location**: `src/types/`
- **Pattern**: Interface naming uses `I{Feature}` prefix

#### Type Template
```tsx
// types/Example.d.ts
interface IExample {
  _id?: string;
  name?: string;
  slug?: string;
  description?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

interface IExampleForm extends IExample {
  additionalField?: string;
}

export type { IExample, IExampleForm };
```

> **Catatan**: Interface didefinisikan tanpa `export` langsung, lalu di-export menggunakan `export type { ... }` di akhir file. Naming menggunakan prefix `I` untuk interface utama dan suffix `Form` untuk form-specific types.

### 7. Utilities & Helper Functions

#### Utility Functions
- **Location**: `src/utils/`
- **File naming**: `{feature}.ts`
- **Exports**: Named exports for utility functions

#### Common Utilities
```tsx
// utils/cn.ts - Tailwind class merging
import { ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// utils/date.ts - Date formatting
const convertTime = (isoDate: string) => {
  const dateObject = new Date(isoDate);
  const date = dateObject.toLocaleString("id-ID", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Jakarta",
  });
  return `${date} WIB`;
};
export { toDateStandard, toInputDate, convertTime };

// utils/currency.ts - Currency formatting
const convertIDR = (value: number) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value);
};
export { convertIDR };
```

> **Catatan**: Utility functions menggunakan `const` + arrow function, dan di-export menggunakan `export { ... }` di akhir file (bukan `export function` atau `export const` langsung).

### 8. Constants Management

#### Structure
- **Global constants**: `src/constants/`
- **Feature constants**: `{Feature}.constants.tsx` in feature folder
- **Naming**: UPPER_SNAKE_CASE for constants

#### Pattern
```tsx
// constants/list.constants.ts
const LIMIT_LISTS = [
  { label: "8", value: 8 },
  { label: "12", value: 12 },
  { label: "16", value: 16 },
];

const LIMIT_DEFAULT = LIMIT_LISTS[0].value;
const PAGE_DEFAULT = 1;
const DELAY = 1000;

export { DELAY, LIMIT_LISTS, LIMIT_DEFAULT, PAGE_DEFAULT };
```

> **Catatan**: Constants didefinisikan sebagai `const` biasa, kemudian di-export menggunakan grouped `export { ... }` di akhir file.

### 9. Styling Standards

#### Tailwind CSS
- **Framework**: TailwindCSS for styling
- **Plugin**: `prettier-plugin-tailwindcss` for class sorting
- **Merge Utility**: Use `cn()` utility for conditional classes
- **Pattern**: Inline classes or component-specific constants

#### Class Ordering Example
```tsx
<div className={cn(
  className,
  "rounded-lg border border-gray-200 bg-white p-4", // layout
  "shadow-sm hover:shadow-md", // effects
  "transition-all duration-200" // animations
)}>
  Content
</div>
```

### 10. Code Quality Standards

#### TypeScript Configuration
- **Mode**: `strict: true`
- **Target**: `ES2022`
- **Path alias**: `@/*` → `./src/*`
- **Module resolution**: `node`

#### ESLint & Prettier
- **ESLint config**: `next/core-web-vitals`
- **Prettier plugins**: `prettier-plugin-tailwindcss`
- **Auto-format**: Run on save in IDE

#### Scripts
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

### 11. Git & Commit Standards

#### Commit Convention
- **Format**: Conventional Commits
- **Tool**: `commitlint` with `@commitlint/config-conventional`
- **Hooks**: `husky` pre-commit hooks

#### Commit Types
```
feat:      A new feature
fix:       A bug fix
docs:      Documentation only changes
style:     Changes that don't affect code meaning
refactor:  Code change that neither fixes a bug nor adds a feature
perf:      Code change that improves performance
test:      Adding missing tests or correcting existing tests
chore:     Changes to build process, dependencies, etc.
```

#### Commit Examples
```
feat: add user authentication with NextAuth
fix: resolve layout shift on banner load
docs: update API documentation
refactor: extract common logic into useForm hook
```

### 12. Dependencies & Versions

#### Core Stack
```json
{
  "@heroui/react": "^2.6.0+",
  "@tanstack/react-query": "^5.0.0+",
  "axios": "^1.7.0+",
  "next": "^15.0.0+",
  "next-auth": "^4.24.0+",
  "react": "^19.0.0+",
  "react-hook-form": "^7.50.0+",
  "yup": "^1.4.0+",
  "tailwindcss": "^3.4.0+",
  "clsx": "^2.1.0+",
  "tailwind-merge": "^2.4.0+"
}
```

#### Dev Dependencies
```json
{
  "@commitlint/cli": "^19.0.0+",
  "@types/react": "^19.0.0+",
  "typescript": "^5.0.0+",
  "eslint": "^9.0.0+",
  "prettier": "^3.3.0+",
  "husky": "^9.0.0+",
  "postcss": "^8.0.0+"
}
```

### 13. State Management Patterns

#### React Query (TanStack Query)
- **Purpose**: Server state management
- **Pattern**: Service layer + custom hooks + `useQuery` / `useMutation`
- **Example**:
```tsx
const { data, isLoading, isRefetching, refetch } = useQuery({
  queryKey: ["Events", currentPage, currentLimit, currentSearch],
  queryFn: () => getEvents(),
  enabled: router.isReady && !!currentPage && !!currentLimit,
});
```

> **Catatan**: `queryKey` menggunakan array dengan dependencies (page, limit, search) agar auto-refetch. `enabled` digunakan untuk menunggu router ready.

#### React Hook Form
- **Purpose**: Form state management
- **Pattern**: With Yup validation
- **Example**:
```tsx
const form = useForm({
  resolver: yupResolver(validationSchema),
  defaultValues: { /* ... */ },
});
```

## 🚀 Project Initialization Checklist

When creating a new project with these standards:

- [ ] Set up folder structure (components, services, types, utils, etc.)
- [ ] Configure TypeScript with strict mode
- [ ] Install core dependencies (Next.js, React, TailwindCSS, etc.)
- [ ] Set up Prettier with tailwindcss plugin
- [ ] Configure ESLint with next/core-web-vitals
- [ ] Initialize Git with husky for pre-commit hooks
- [ ] Configure commitlint for conventional commits
- [ ] Create .env.example with required environment variables
- [ ] Set up API base URL and axios instance
- [ ] Create README with project documentation
- [ ] Set up authentication (NextAuth or alternative)
- [ ] Implement error handling in services
- [ ] Create global constants and utilities
- [ ] Document API endpoints in endpoint.constant.ts

## 📝 Best Practices

### Behavioral Standards (dari LSH Group Guidelines)
1. **Read before you modify** — selalu pahami existing code sebelum suggest perubahan. Jangan blindly accept AI-generated modifications.
2. **Don't over-engineer** — selesaikan masalah yang ada, bukan masalah hipotesis di masa depan. Tiga baris code serupa lebih baik dari premature abstraction.
3. **Don't add what wasn't asked** — bug fix tidak perlu surrounding code di-cleanup. Simple feature tidak perlu extra configurability.
4. **Integrate, don't accumulate** — sebelum membuat script baru, cek apakah yang existing sudah 80% memenuhi kebutuhan. Update file yang ada daripada membuat duplikat.
5. **Test alongside, not after** — tulis test cases bersama dengan feature, bukan sebagai afterthought.
6. **Security first** — selalu pertimbangkan implikasi keamanan sebelum convenience atau speed.

### Quality Requirements (dari LSH Group Standards)
1. **Production-ready** — no pseudo-code, no placeholders, no "TODO" blocks di delivered work
2. **Error-handled** — include error checking, exit codes, dan graceful failure
3. **Commented** — explain setiap significant block of logic. Comments harus explain **why**, bukan hanya **what**
4. **Rollback-ready** — setiap deployment/infrastructure change harus punya rollback procedure
5. **Validated** — include pre-execution checks (dry-run, syntax validation)

### Do's ✅
- Use custom hooks to separate logic from UI
- Keep components small and focused (single responsibility)
- Use TypeScript interfaces for all props
- Centralize API calls in services layer
- Use utility functions for repeated logic
- Organize imports at the top: React, libraries, internal
- Use Fragment for multiple JSX returns
- Handle loading states with skeletons/spinners
- Document complex logic with comments (explain **why**)
- Test critical business logic
- Sertakan file header block di setiap file baru
- Sertakan AI transparency note saat sharing work
- Review terhadap OWASP Top 10 untuk security-sensitive code
- Match review effort to risk level (Gate 6)

### Don'ts ❌
- Don't put API calls directly in components
- Don't use `any` type in TypeScript
- Don't create prop drilling chains (use hooks or context)
- Don't hardcode values (use constants) — **terutama secrets/credentials**
- Don't mix concerns (logic + UI in one file)
- Don't use anonymous functions in JSX
- Don't ignore error handling in API calls
- Don't create deeply nested folder structures
- Don't reuse component names across features
- Don't commit commented-out code
- Don't ship code yang tidak bisa Anda jelaskan (Gate 2)
- Don't over-engineer atau add features yang tidak diminta
- Don't generate scripts yang download dan pipe ke shell
- Don't present uncertain work sebagai confident

## 🔄 Common Patterns

### Modal Component Pattern
```tsx
// components/views/Feature/AddFeatureModal/AddFeatureModal.tsx
interface PropTypes {
  isOpen: boolean;
  onClose: () => void;
}

const AddFeatureModal = (props: PropTypes) => {
  const { isOpen, onClose } = props;
  const { handleSubmit, form } = useAddFeatureModal();

  return (
    <Modal isOpen={isOpen} onOpenChange={onClose}>
      <ModalContent>
        <ModalHeader>Add Feature</ModalHeader>
        <ModalBody>
          <form onSubmit={handleSubmit}>
            {/* Form fields */}
          </form>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default AddFeatureModal;
```

### Data Table Pattern
```tsx
// components/ui/DataTable/DataTable.tsx
interface PropTypes {
  data: any[];
  columns: TableColumn[];
  isLoading?: boolean;
  isPaginated?: boolean;
}

const DataTable = (props: PropTypes) => {
  const { data, columns, isLoading, isPaginated } = props;

  return (
    <Table>
      {/* Table implementation */}
    </Table>
  );
};
```

### Tab Component Pattern
```tsx
// Use nested folders for tab components
// Feature/FeatureDetail/TabName/TabName.tsx
// Feature/FeatureDetail/TabName/index.tsx
// Feature/FeatureDetail/TabName/useTabName.tsx
```

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Best Practices](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [HeroUI Components](https://heroui.com)
- [TanStack Query Documentation](https://tanstack.com/query)
- [React Hook Form Documentation](https://react-hook-form.com)

## 🤝 Contributing

When contributing to projects using these standards:
1. Follow the established folder structure
2. Maintain consistent naming conventions
3. Write meaningful commit messages using conventional commits
4. Ensure TypeScript builds without errors
5. Format code with Prettier
6. Pass ESLint checks
7. Add type definitions for all props and returns
8. Sertakan file header block di setiap file baru
9. Sertakan AI transparency note jika AI-assisted
10. Review security implications sebelum merge (Gate 1)
11. Pastikan bisa explain semua code yang ditulis (Gate 2)
12. Check apakah file serupa sudah ada sebelum buat baru (Gate 3)

---

**LSH Group Policy References:**
- AI-Assisted Development Standards v1.0 (31 March 2026)
- AI Development Discipline Framework v1.0 (31 March 2026)
- Issued by: Afif Kamal Fiska, Regional IT Manager
- Applies to: All IT staff across ID, SG, CN

**Last Updated**: 2026-04-13
**Version**: 2.0.0

Produced with AI assistance | Reviewed by: [Your Name]
