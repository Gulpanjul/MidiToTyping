# Clean Code Quick Reference

Cheat sheet singkat untuk standar clean code fe-acara.

## 📁 Folder Organization

```
components/
  ├── commons/         ← Shared components (AppShell, PageHead)
  ├── layouts/         ← Page layouts
  ├── ui/              ← Presentational components
  └── views/           ← Page-specific components with logic
config/               ← Environment configuration
services/             ← API calls & business logic
types/                ← TypeScript interfaces (.d.ts)
utils/                ← Helper functions (cn, currency, date)
libs/axios/           ← HTTP instance & response handler
hooks/                ← Global custom hooks (useChangeUrl, useDebounce)
constants/            ← Global constants (list.constants.ts)
pages/                ← Next.js Pages Router
```

## 🧩 Component Template

```tsx
interface PropTypes {
  className?: string;
  title: string;
}

const Component = (props: PropTypes) => {
  const { className, title } = props;
  return <div className={cn(className, "base")}>{title}</div>;
};

export default Component;
```

## 📤 Index File Export

```tsx
// components/Feature/index.tsx
import Feature from "./Feature";

export default Feature;
```

## 🔗 Service Template

```tsx
const featureServices = {
  getFeatures: (params?: string) => instance.get(`${endpoint.FEATURE}?${params}`),
  getFeatureById: (id: string) => instance.get(`${endpoint.FEATURE}/${id}`),
  addFeature: (payload: IFeature) => instance.post(endpoint.FEATURE, payload),
  updateFeature: (id: string, payload: IFeature) => 
    instance.put(`${endpoint.FEATURE}/${id}`, payload),
  deleteFeature: (id: string) => instance.delete(`${endpoint.FEATURE}/${id}`),
};

export default featureServices;
```

## 🪝 Hook Template (View-level with React Query)

```tsx
const useFeature = () => {
  const [selectedId, setSelectedId] = useState<string>("");
  const router = useRouter();
  const { currentLimit, currentPage, currentSearch } = useChangeUrl();

  const getFeatures = async () => {
    let params = `limit=${currentLimit}&page=${currentPage}`;
    if (currentSearch) params += `&search=${currentSearch}`;
    const res = await featureServices.getFeatures(params);
    return res.data;
  };

  const { data, isLoading, isRefetching, refetch } = useQuery({
    queryKey: ["Features", currentPage, currentLimit, currentSearch],
    queryFn: () => getFeatures(),
    enabled: router.isReady && !!currentPage && !!currentLimit,
  });

  return { data, isLoading, isRefetching, refetch, selectedId, setSelectedId };
};

export default useFeature;
```

## 📝 Type Template

```tsx
// types/Feature.d.ts
interface IFeature {
  _id?: string;
  name?: string;
  description?: string;
}

interface IFeatureForm extends IFeature {
  additionalField?: string;
}

export type { IFeature, IFeatureForm };
```

## 🎨 Styling Patterns

```tsx
// Conditional classes
<div className={cn("base-class", condition && "conditional-class")}>

// Multiple conditions
<div className={cn(
  className,
  "layout-classes",
  isActive && "active-classes",
  isLoading && "loading-classes"
)}>
```

## 🔤 Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Components | PascalCase | `MyComponent`, `CardEvent` |
| Hooks | use + PascalCase | `useFeature`, `useFetch` |
| Services | {feature}.service.ts | `event.service.ts` |
| Types | I + Feature | `IEvent`, `IUser` |
| Constants | UPPER_SNAKE_CASE | `API_URL`, `MAX_ITEMS` |
| Props Interface | PropTypes | `interface PropTypes` |
| Utilities | camelCase | `convertIDR`, `convertTime` |

## 📦 Key Dependencies

```json
{
  "next": "^15.1.1",
  "react": "^19.0.0",
  "typescript": "^5",
  "tailwindcss": "^3.4.1",
  "@heroui/react": "^2.6.14",
  "@tanstack/react-query": "^5.62.8",
  "axios": "^1.7.2",
  "react-hook-form": "^7.52.1",
  "yup": "^1.4.0",
  "next-auth": "^4.24.11"
}
```

## 🏢 LSH Group Standards (Wajib)

### File Header Block
```tsx
// ============================================================
// File: [filename]
// Date: [YYYY-MM-DD]
// Author: [Your name and role]
// Task: [Brief description]
// AI-Assisted: [Yes/No — if Yes, which tool]
// ============================================================
```

### AI Transparency Footer
```
Produced with AI assistance | Reviewed by: [Your Name]
```

### 4Ds Quick Reference
| D | Principle | One-liner |
|---|-----------|-----------|
| D1 | Delegation | Right task, right mode, right tool |
| D2 | Description | Understand intent, not just instruction |
| D3 | Discernment | Surface problems, don't hide them |
| D4 | Diligence | Own what you produce |

### 6 Gates Quick Reference
| Gate | One-liner |
|------|-----------|
| G1 Security | Untrusted until proven safe |
| G2 Comprehension | Never deliver what you can't explain |
| G3 Tech Debt | Search before you create |
| G4 Perception | Measure reality, not feeling |
| G5 Scope | Define boundary before you start |
| G6 Risk Tier | Match review to risk level |

### Security Rules
- **No hardcoded secrets** — use `<REPLACE_WITH_API_KEY>`
- **No PII in examples** — use synthetic data
- **Error handling wajib** — graceful failure behavior
- **Rollback-ready** — every change harus punya rollback

## ✅ Do's & Don'ts

### ✅ DO
- Use `interface PropTypes` for all props
- Separate logic in custom hooks
- Put API calls in services layer
- Use `cn()` for conditional classes
- Type everything with TypeScript
- Use `Fragment` for multiple JSX returns
- Sertakan file header block di setiap file baru
- Review terhadap OWASP Top 10 untuk security code
- Read before you modify (understand existing code first)
- Comments yang explain **why**, bukan hanya **what**

### ❌ DON'T
- Use `any` type
- Hardcode values — **terutama secrets/credentials**
- Put API calls in components
- Use prop drilling chains
- Create anonymous functions in JSX
- Leave commented code
- Ship code yang tidak bisa Anda jelaskan (Gate 2)
- Over-engineer atau add features yang tidak diminta
- Blindly accept AI-generated modifications
- Present uncertain work sebagai confident

## 🔧 Common Commands

```bash
# Development
npm run dev                 # Start dev server

# Build & Production
npm run build              # Build for production
npm run start              # Start production server

# Quality
npm run lint               # Run ESLint

# Git
git commit -m "feat: add feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update docs"
git commit -m "refactor: extract logic"
```

## 🎯 File Organization Examples

### Simple Component
```
Button/
  ├── Button.tsx
  └── index.tsx
```

### Component with Logic
```
Feature/
  ├── Feature.tsx
  ├── Feature.constants.tsx
  ├── useFeature.ts
  └── index.tsx
```

### Complex Component with Subcomponents
```
Feature/
  ├── Feature.tsx
  ├── Feature.constants.tsx
  ├── useFeature.ts
  ├── Modal/
  │   ├── Modal.tsx
  │   ├── useModal.ts
  │   └── index.tsx
  ├── Tabs/
  │   └── Tab1/
  │       ├── Tab1.tsx
  │       ├── useTab1.ts
  │       └── index.tsx
  └── index.tsx
```

## 📊 Component Type Decision Tree

```
Is it reusable across pages?
  → YES: Place in components/commons/ or components/ui/
  → NO: Place in components/views/

Does it contain page layout?
  → YES: Place in components/layouts/

Is it mostly presentational (just takes props)?
  → YES: Place in components/ui/

Does it have business logic?
  → YES: Create useComponent.ts hook
  → Place in components/views/

Does it have feature-specific constants?
  → YES: Create Component.constants.tsx
```

## 🔄 Common Patterns Quick Copy

### Form with Validation
```tsx
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: yupResolver(validationSchema),
});

<form onSubmit={handleSubmit(onSubmit)}>
  <input {...register("fieldName")} />
  {errors.fieldName && <span>{errors.fieldName.message}</span>}
</form>
```

### React Query Hook
```tsx
const { data, isLoading, isRefetching, refetch } = useQuery({
  queryKey: ["Features", currentPage, currentLimit, currentSearch],
  queryFn: () => getFeatures(),
  enabled: router.isReady && !!currentPage && !!currentLimit,
});
```

### Modal Pattern
```tsx
const [isOpen, setIsOpen] = useState(false);

<Button onPress={() => setIsOpen(true)}>Open</Button>
<Modal isOpen={isOpen} onOpenChange={setIsOpen}>
  <ModalContent>{/* content */}</ModalContent>
</Modal>
```

### Conditional Rendering
```tsx
{!isLoading ? (
  <div>{data}</div>
) : (
  <Skeleton />
)}
```

## 🚀 Setup Checklist

New project must have:
- [ ] TypeScript strict mode
- [ ] Path alias @/*
- [ ] TailwindCSS with Prettier plugin
- [ ] ESLint with next/core-web-vitals
- [ ] .prettierrc configuration
- [ ] tsconfig.json setup
- [ ] commitlint + husky
- [ ] .env.example
- [ ] Example service
- [ ] Example hook
- [ ] Example component
- [ ] README.md

## 📚 Where to Look

| Need | Look at |
|------|---------|
| Component structure | `src/components/commons/` |
| Complex component | `src/components/views/Admin/` |
| Service pattern | `src/services/event.service.ts` |
| API instance | `src/libs/axios/instance.ts` |
| Environment config | `src/config/environment.ts` |
| Type definitions | `src/types/Event.d.ts` |
| Utilities | `src/utils/cn.ts` |
| Global hooks | `src/hooks/useChangeUrl.tsx` |
| View-level hooks | `src/components/views/*/use*.ts` |
| Constants | `src/constants/list.constants.ts` |

## 🔗 Import Examples

```tsx
// Service
import featureServices from "@/services/feature.service";

// Type
import type { IFeature } from "@/types/Feature";

// Utility
import { cn } from "@/utils/cn";
import { convertIDR } from "@/utils/currency";
import { convertTime } from "@/utils/date";

// Global hook
import useChangeUrl from "@/hooks/useChangeUrl";
import useDebounce from "@/hooks/useDebounce";

// View-level hook (relative import)
import useFeature from "./useFeature";

// Environment config
import environment from "@/config/environment";
```

## ⚡ Performance Tips

```tsx
// ✅ Good: Memoized callback
const handleClick = useCallback(() => {}, [deps]);

// ✅ Good: Skeleton loader
{isLoading && <Skeleton />}

// ✅ Good: Image optimization
<Image src={url} width={1920} height={1080} />

// ❌ Avoid: Anonymous function
<Button onClick={() => doSomething()} />

// ❌ Avoid: Inline object props
<Component config={{ a: 1, b: 2 }} />
```

---

**Quick Reference Version**: 1.0.0
**Last Updated**: 2026-04-13

*For detailed documentation, see [LSH_FRONTEND_STANDARDS.md](LSH_FRONTEND_STANDARDS.md)*
