# Add New Section Type

Guide to add a new content section type end-to-end.

Ask the user: "What's the name of the new section type? (e.g., 'gallery', 'team', 'faq')"

Once you have the section type name, do ALL of the following:

## 1. Backend: Add JSON Schema (backend/src/schemas/content.py)

Add a new Pydantic model for the section type following existing patterns.
Example for a `team` section:
```python
class TeamSectionContent(BaseModel):
    headline: Optional[str] = None
    items: list[TeamMember]

class TeamMember(BaseModel):
    name: str
    role: str
    bio: Optional[str] = None
    avatar_emoji: Optional[str] = None
```

Register it in the `SECTION_SCHEMAS` dict and `parse_section_content()` function.

## 2. Frontend: Create Section Component (frontend/src/components/sections/)

Create `{TypeName}Section.tsx` following the patterns of existing section components.
- Parse the JSON content
- Use TailwindCSS with CSS variable-based theme colors (var(--color-primary), etc.)
- Include CSS scroll animation class `animate-on-scroll`
- Handle missing/partial data gracefully

## 3. Frontend: Register in Site Renderer (frontend/src/app/[site_slug]/page.tsx)

Add the new section type to the `SECTION_COMPONENTS` mapper:
```typescript
const SECTION_COMPONENTS = {
  // ... existing types
  [section_type]: NewSection,
}
```

## 4. Frontend: Add Admin Form (frontend/src/components/admin/section-editor/)

Create `{TypeName}SectionForm.tsx` with structured input fields matching the schema.
Register in the section editor mapper.

## 5. MCP: Update Tool Description (mcp_server/src/aicms_mcp_server/server.py)

Add the new section type to the `update_page_content` tool description with a JSON example.

## 6. Documentation (docs/content-schema.md)

Add a new section documenting:
- JSON schema with all fields, required/optional, descriptions
- Example JSON
- Notes on rendering behavior

## 7. Test

- Restart backend: `./cli.sh restart-backend`
- Restart frontend: `./cli.sh restart-frontend`
- Create a section via MCP and verify it renders correctly
- Run tests: `./cli.sh test`
