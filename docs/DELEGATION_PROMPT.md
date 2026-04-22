# Delegation Prompt for New Frontend Projects

Gunakan prompt berikut untuk mendelegasikan pembuatan project frontend baru dengan standar clean code fe-acara.

## 🎯 Complete Project Brief Prompt

Copy & paste prompt ini ke Claude Code untuk membuat project baru:

---

### Prompt Template

```
Create a new Next.js frontend project named "[PROJECT_NAME]" with the following specifications.

📋 ARCHITECTURE & STRUCTURE:
- Follow the exact folder structure from fe-acara: 
  components/(commons, layouts, ui, views), 
  config,
  libs/axios, 
  services, 
  types, 
  utils, 
  hooks, 
  constants
- Each component has an index.tsx that re-exports via: import X; export default X
- Services are grouped by feature with CRUD methods pattern
- Types use .d.ts extension with I{Feature} naming prefix
- Utilities are organized by purpose (cn, currency, date, etc.)
- Config centralizes all environment variables (no direct process.env access)

💻 TECHNOLOGY STACK:
- Next.js 15.1.1+
- React 19.0.0+
- TypeScript with strict mode enabled
- TailwindCSS with Prettier plugin for class sorting
- HeroUI for component library
- React Query (TanStack Query) for server state
- Axios with custom instance
- NextAuth for authentication
- React Hook Form + Yup for form handling
- Husky + Commitlint for git hooks

🏗️ CODE PATTERNS TO FOLLOW:
1. Component Props: Use `interface PropTypes` pattern, always destructure props
2. Custom Hooks: File naming convention `use{Feature}.ts`, export business logic separately
3. Services: Object with methods like getFeatures(), addFeature(), updateFeature(), deleteFeature()
4. Types: Interface with I{Feature} prefix, export in {Feature}.d.ts files
5. Utilities: Pure functions for common operations (formatting, validation, etc.)
6. Styling: Use cn() utility function for conditional Tailwind classes
7. Constants: UPPER_SNAKE_CASE for globals, feature-specific in {Feature}.constants.tsx

⚙️ CONFIGURATION:
- Setup TypeScript with path alias @/* → src/*
- ESLint extending next/core-web-vitals (disable react-hooks/exhaustive-deps)
- Prettier with prettier-plugin-tailwindcss
- Conventional Commits with commitlint
- Git hooks with husky (pre-commit: lint, commit-msg: commitlint)

📝 SETUP TASKS:
- Initialize Next.js with TypeScript & TailwindCSS
- Create folder structure matching the template
- Setup axios instance with request/response interceptors
- Create example service, hook, component, and type following patterns
- Setup .env.example with required variables
- Create comprehensive README.md
- Create CLAUDE.md documenting these standards
- Create PROJECT_TEMPLATE.md with setup instructions
- Initialize git with conventional commits

🎨 INITIAL COMPONENTS TO CREATE:
- One commons component (reusable layout element)
- One UI component (Card, Button, etc.)
- One view component with modal (CRUD example)
- One custom hook (data fetching with React Query)

🏢 LSH GROUP IT STANDARDS (Wajib):
- File header block di setiap file baru (File, Date, Author, Task, AI-Assisted)
- AI transparency footer: "Produced with AI assistance | Reviewed by: [Name]"
- No hardcoded secrets — gunakan placeholder <REPLACE_WITH_API_KEY>
- No PII in examples — gunakan data sintetis
- Review terhadap OWASP Top 10 untuk security-sensitive code
- Ikuti 4D Protocol: Delegation, Description, Discernment, Diligence
- Ikuti 6-Gate Protocol: Security, Comprehension, Technical Debt, Perception, Scope, Risk-Tiered Review
- Read before modify — pahami existing code sebelum ubah
- Don't over-engineer — solve actual problem, not hypothetical
- Integrate, don't accumulate — update existing, don't duplicate

✅ QUALITY STANDARDS:
- TypeScript strict mode - no 'any' types
- All props must have PropTypes interface
- All functions must be typed (no implicit any)
- Services abstract all API calls
- Custom hooks separate logic from UI
- Error handling in all async operations (graceful failure)
- Proper loading/error states
- Semantic HTML
- Accessible component patterns
- Production-ready: no pseudo-code, no "TODO" blocks
- Comments explain WHY, not just WHAT
- Rollback-ready for deployment scripts

🔍 FINAL CHECKS:
- npm run build succeeds without errors
- npm run lint passes without warnings
- All imports use @/* alias correctly
- Git commits follow conventional format
- README explains project purpose and setup
- .env.example has all required variables
- No console.log statements left in production code
- Components are properly organized by type
- All style classes properly sorted by Prettier

Reference documentation: See [LSH_FRONTEND_STANDARDS.md](LSH_FRONTEND_STANDARDS.md) in docs/ for complete standards.
```

---

## 🔄 Alternative: Concise Version (For Quick Projects)

Jika ingin lebih ringkas:

```
Create a new Next.js project "[PROJECT_NAME]" using fe-acara as architectural reference.

Key points:
- Folder structure: components/(commons, layouts, ui, views), libs, services, types, utils, hooks
- Stack: Next.js 15, React 19, TypeScript strict, TailwindCSS, HeroUI, React Query, Axios
- Patterns: PropTypes interfaces, custom hooks with use* prefix, services with CRUD methods
- Config: Path alias @/*, ESLint next/core-web-vitals, Prettier + tailwindcss plugin
- Git: Conventional commits with commitlint + husky hooks

Create example component, service, hook, and type demonstrating patterns.
Setup .env.example, README.md, and initialize git repository.
```

---

## 📋 Follow-up Questions Template

Jika ada ambiguitas, tanyakan pertanyaan berikut sebelum memulai:

```
Sebelum membuat project, clarify:

1. Project Name: [name]
2. Primary Features: [list main features]
3. Authentication Type: NextAuth / Custom / None
4. State Management: React Query (default) / Redux / Context / Other
5. UI Library: HeroUI (default) / Shadcn / Material / Other
6. Database/Backend: [API endpoint or backend URL]
7. Deployment Target: Vercel / Other
8. Additional Packages Needed: [specify if any beyond standard stack]
9. Initial Pages/Routes: [list main routes needed]
10. Design System: [colors, fonts, specific design requirements]
```

---

## 🚀 Quick Reference Matrix

Gunakan tabel ini untuk quick reference saat delegating:

| Aspect | Specification |
|--------|---------------|
| **Framework** | Next.js 15+ with TypeScript strict |
| **Styling** | TailwindCSS + Prettier plugin |
| **UI Library** | HeroUI 2.6+ |
| **State (Server)** | React Query v5+ |
| **State (Form)** | React Hook Form + Yup |
| **HTTP Client** | Axios with custom instance |
| **Auth** | NextAuth v4+ |
| **Component Pattern** | Props interface + destructure |
| **Hook Pattern** | use{Feature}.ts + business logic |
| **Service Pattern** | Object with CRUD methods |
| **Types** | I{Feature}.d.ts in src/types/ |
| **Utils** | Pure functions by purpose |
| **Git** | Conventional Commits |
| **Linting** | ESLint next/core-web-vitals |
| **Formatting** | Prettier + tailwindcss plugin |

---

## 📦 Minimal Setup Checklist

Jika project sudah dibuat, pastikan:

- [ ] Folder structure matches template
- [ ] TypeScript compiles (strict mode)
- [ ] npm run lint passes
- [ ] .env.example created
- [ ] README.md complete
- [ ] Git initialized with first commit
- [ ] Example component created
- [ ] Example service created
- [ ] Example hook created
- [ ] .prettierrc configured
- [ ] .eslintrc.json configured
- [ ] tsconfig.json path alias set
- [ ] Husky hooks installed
- [ ] Next.js builds successfully

---

## 🎓 Learning Resources to Include

Saat membuat project baru, refer to:

1. **Project Documentation**
   - LSH_FRONTEND_STANDARDS.md (full standards)
   - PROJECT_TEMPLATE.md (setup guide)
   - README.md (specific project docs)

2. **Component Examples**
   - Look at fe-acara components/commons for patterns
   - Look at fe-acara components/ui for UI patterns
   - Look at fe-acara components/views for complex patterns

3. **Service Examples**
   - Check fe-acara services/ for API integration patterns
   - Review fe-acara libs/axios/ for HTTP setup

4. **Type Examples**
   - Reference fe-acara types/ for TypeScript patterns
   - Follow naming convention I{Feature}

---

## 🔗 Integration Points

When delegating, point to these resources:

```
Reference these fe-acara files for architectural patterns:
- src/components/commons/ → component structure
- src/components/views/ → complex component patterns
- src/services/event.service.ts → service pattern
- src/types/Event.d.ts → type definition pattern
- src/utils/cn.ts → utility pattern
- LSH_FRONTEND_STANDARDS.md → complete standards documentation
```

---

## 💡 Common Customizations

When delegating, you may need to customize:

### 1. Different UI Library
```
Replace HeroUI with [Library]
- Update imports in components
- Adjust component patterns
- Update button/form components accordingly
```

### 2. Different State Management
```
Replace React Query with [Library]
- Update hook patterns in components/views
- Modify service layer structure if needed
```

### 3. Different Authentication
```
Replace NextAuth with [Auth Solution]
- Update libs/axios/instance.ts
- Create new auth service
- Adjust middleware/routing
```

### 4. Additional Pages/Features
```
Create pages for:
- [Feature 1] in pages/[feature1]
- [Feature 2] in pages/[feature2]
- Follow component structure guidelines
```

---

**Prompt Version**: 1.0.0
**Last Updated**: 2026-04-13
**For Project**: fe-acara
