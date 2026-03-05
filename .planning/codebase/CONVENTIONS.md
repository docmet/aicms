# Conventions

## Code Style

### Frontend
- **Formatter**: Prettier 3.4 (`prettier.config.json`)
- **Linter**: ESLint 8.57 (`.eslintrc.json`, Next.js rules)
- **Typecheck**: `tsc --noEmit`
- **Test**: Vitest 2.1

### Backend
- **Formatter**: Black (88-char line length)
- **Import sort**: isort with `profile = "black"`
- **Linter**: Ruff (rules: E, F, I, N, W, UP)
- **Typecheck**: mypy 1.13+ (strict)
- **Test**: pytest + pytest-asyncio

### Run via CLI (never raw tools)
```bash
./cli.sh lint         # ESLint + ruff
./cli.sh typecheck    # tsc + mypy
./cli.sh test         # vitest run + pytest
```

## Naming Conventions

### TypeScript / Frontend
- **Components**: `PascalCase` (e.g., `HeroSection`, `SiteNavBar`)
- **Hooks**: `useHookName` function, `use-hook-name.ts` file
- **Utilities**: `camelCase.ts`
- **CSS classes**: Tailwind utility classes; custom via `globals.css`
- **Import alias**: `@/` maps to `src/` (always use alias, never relative `../`)

### Python / Backend
- **Classes**: `PascalCase` (models, schemas, exceptions)
- **Functions/variables**: `snake_case`
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `PLAN_SITE_LIMITS`)
- **Enums**: `snake_case` values (`UserPlan.free`, `UserPlan.pro`)
- **DB tables**: `snake_case` plural (e.g., `content_sections`)

## TypeScript Patterns

### Client Components
```tsx
"use client"  // required for hooks/interactivity

interface Props {
  siteId: string
  onSave?: () => void
}

export function SiteEditor({ siteId, onSave }: Props) { ... }
```

### Utility styling
```tsx
import { cn } from "@/lib/utils"
<div className={cn("base-classes", isActive && "active-class")} />
```

### Toasts
```tsx
import { useToast } from "@/hooks/use-toast"  // NOT from @/components/ui/
const { toast } = useToast()
toast({ title: "Saved", description: "Site updated." })
```

## Python / Pydantic Patterns

### Schema pattern
```python
class SiteCreate(BaseModel):
    name: str
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    theme: str = "modern"

class SiteResponse(BaseModel):
    id: int
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)
```

### Router pattern
```python
router = APIRouter(prefix="/sites", tags=["sites"])

@router.post("/", response_model=SiteResponse, status_code=201)
async def create_site(
    data: SiteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
): ...
```

### Async DB pattern
```python
result = await db.execute(select(Site).where(Site.user_id == user.id))
site = result.scalar_one_or_none()
if not site:
    raise HTTPException(status_code=404, detail="Site not found")
```

## Error Handling

### Backend
- Use `HTTPException(status_code=N, detail="message")` for API errors
- Structured error codes for frontend parsing: `plan_limit_reached:{plan}:{limit}`
- No bare `except Exception:` — always log context before re-raising
- 404 for missing resources, 403 for permission failures, 400 for validation

### Frontend
- `try/catch` around API calls
- Show toast on error
- Never expose raw error objects to users

## API Conventions
- Routes: `/api/{resource}` (NOT `/api/v1/`) — historical v1 routes all removed
- Auth: `POST /api/auth/login` accepts **form data** (not JSON)
- List responses: return arrays directly (not paginated envelope — yet)
- Content-Type: `application/json` for all except auth login (multipart form)
- Soft deletes: `is_deleted` flag, never hard delete (except explicit user delete)

## Component Patterns

### Section components
```tsx
// All section components accept content as typed props
interface HeroSectionProps {
  content: HeroContent
  theme?: string
}
export function HeroSection({ content }: HeroSectionProps) { ... }
```

### Section registry (`frontend/src/components/sections/index.ts`)
```ts
export const SECTION_COMPONENTS: Record<string, React.ComponentType<SectionProps>> = {
  hero: HeroSection,
  features: FeaturesSection,
  // ...
}
```

## Git Conventions
- **Commits**: Conventional Commits format — `feat(scope):`, `fix(scope):`, `docs(scope):`
- **Branch strategy**: commit directly to `main` — no feature branches
- **Hooks**: lefthook runs lint → typecheck → test on pre-commit
- **Never**: `--no-verify`, amend published commits, force-push to main

## Content Model Conventions
- MCP writes to `content_draft` only — never `content_published`
- Publish explicitly via `POST /api/sites/{id}/pages/{id}/publish`
- Section upsert (create-or-update): `PUT /api/sites/{id}/pages/{id}/content/by-type/{type}`
- All section JSON must match its Pydantic schema in `backend/src/schemas/content.py`
