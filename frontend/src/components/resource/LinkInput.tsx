"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
// Using Frappe's search_link endpoint for multi-field search (respects search_fields/title_field)

function useDebouncedValue<T>(value: T, delay = 300) {
  const [debounced, setDebounced] = React.useState(value)
  React.useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

export interface LinkInputProps {
  value: string
  onChange: (val: string) => void
  linkDoctype: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
}

export function LinkInput({ value, onChange, linkDoctype, placeholder, disabled, required }: LinkInputProps) {
  const [open, setOpen] = React.useState(false)
  const [query, setQuery] = React.useState("")
  const debounced = useDebouncedValue(query, 300)
  const [options, setOptions] = React.useState<Array<{ value: string; description?: string }>>([])
  const [loading, setLoading] = React.useState(false)
  const containerRef = React.useRef<HTMLDivElement | null>(null)

  React.useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current) return
      if (!containerRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", onDocClick)
    return () => document.removeEventListener("mousedown", onDocClick)
  }, [])

  React.useEffect(() => {
    let ignore = false
    async function run() {
      if (!debounced) { setOptions([]); return }
      setLoading(true)
      try {
        const url = `/api/method/frappe.desk.search.search_link?doctype=${encodeURIComponent(linkDoctype)}&txt=${encodeURIComponent(debounced)}&limit=10`
        const res = await fetch(url)
        const json = await res.json()
        const rows = (json?.message || []) as Array<{ value: string; description?: string }>
        if (!ignore) setOptions(rows)
      } catch (e) {
        if (!ignore) setOptions([])
      } finally {
        if (!ignore) setLoading(false)
      }
    }
    run()
    return () => { ignore = true }
  }, [debounced, linkDoctype])

  return (
    <div ref={containerRef} className="relative">
      <Input
        value={value}
        onChange={(e) => { setQuery(e.target.value); onChange(e.target.value); setOpen(true) }}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        onFocus={() => setOpen(true)}
      />
      {open && (query || options.length > 0) && (
        <div className="absolute z-20 mt-1 w-full overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md">
          {loading ? (
            <div className="p-2 text-sm text-muted-foreground">Searching...</div>
          ) : options.length === 0 ? (
            <div className="p-2 text-sm text-muted-foreground">No results</div>
          ) : (
            <ul className="max-h-60 overflow-auto">
              {options.map((opt) => (
                <li
                  key={opt.value}
                  className="cursor-pointer px-3 py-2 text-sm hover:bg-accent hover:text-accent-foreground"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => { onChange(opt.value); setQuery(opt.value); setOpen(false) }}
                >
                  <div className="font-medium">{opt.description || opt.value}</div>
                  <div className="text-xs text-muted-foreground">{opt.value}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
