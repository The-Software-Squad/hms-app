"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { ResourceField } from "@/hooks/useResourceConfig"
import { LinkInput } from "./LinkInput"

function getDoctypeFromBoot(doctype: string): { fields?: ResourceField[], title_field?: string, list_view_fields?: string[] } | null {
  const boot = (window as any)?.frappe?.boot
  const hms = boot?.hms_doctypes
  if (hms && hms[doctype]) return hms[doctype]
  const doctypes = boot?.doctypes
  if (doctypes && doctypes[doctype]) return doctypes[doctype]
  return null
}

export interface ChildTableEditorProps {
  value: Array<Record<string, any>>
  onChange: (rows: Array<Record<string, any>>) => void
  childDoctype: string
  parentField: string
}

export function ChildTableEditor({ value, onChange, childDoctype }: ChildTableEditorProps) {
  const cfg = getDoctypeFromBoot(childDoctype)
  const fields = (cfg?.fields || []) as ResourceField[]
  const effectiveFields = React.useMemo(
    () => fields.filter((f) => !f.hidden && f.fieldtype !== 'Section Break' && f.fieldtype !== 'Column Break'),
    [fields]
  )
  const listFields = (cfg?.list_view_fields && cfg.list_view_fields.length > 0)
    ? cfg.list_view_fields.filter((f) => f !== 'name')
    : effectiveFields.filter((f) => f.in_list_view && f.fieldname !== 'name').map(f => f.fieldname)
  let shown = effectiveFields.filter((f) => listFields.includes(f.fieldname))
  if (shown.length === 0) {
    // Fallback: take first few non-hidden fields if none configured for list view
    shown = effectiveFields.slice(0, 5)
  }

  const [editingIndex, setEditingIndex] = React.useState<number | null>(null)
  const [draft, setDraft] = React.useState<Record<string, any>>({})

  const openEditor = (idx: number) => {
    setEditingIndex(idx)
    setDraft({ ...(value?.[idx] || {}) })
  }

  const closeEditor = () => {
    setEditingIndex(null)
    setDraft({})
  }

  const saveEditor = () => {
    if (editingIndex === null) return
    const rows = [...(value || [])]
    rows[editingIndex] = { ...(rows[editingIndex] || {}), ...draft }
    onChange(rows)
    closeEditor()
  }

  const deleteEditor = () => {
    if (editingIndex === null) return
    const rows = [...(value || [])]
    rows.splice(editingIndex, 1)
    onChange(rows)
    closeEditor()
  }

  const renderEditorField = (f: ResourceField) => {
    // Show all non-hidden fields in modal
    if (f.hidden) return null
    const v = draft[f.fieldname] ?? ""
    if (f.fieldtype === 'Date') {
      return (
        <div key={f.fieldname} className="space-y-2">
          <Label htmlFor={f.fieldname}>{f.label}</Label>
          <Input id={f.fieldname} type="date" value={v} onChange={(e) => setDraft({ ...draft, [f.fieldname]: e.target.value })} />
        </div>
      )
    }
    if (f.fieldtype === 'Int' || f.fieldtype === 'Float' || f.fieldtype === 'Currency') {
      return (
        <div key={f.fieldname} className="space-y-2">
          <Label htmlFor={f.fieldname}>{f.label}</Label>
          <Input id={f.fieldname} type="number" value={v} onChange={(e) => setDraft({ ...draft, [f.fieldname]: e.target.value })} />
        </div>
      )
    }
    if (f.fieldtype === 'Select') {
      const opts = f.options?.split('\n') || []
      return (
        <div key={f.fieldname} className="space-y-2">
          <Label htmlFor={f.fieldname}>{f.label}</Label>
          <select
            id={f.fieldname}
            value={v}
            onChange={(e) => setDraft({ ...draft, [f.fieldname]: e.target.value })}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option value="">Select {f.label}</option>
            {opts.map((o) => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
      )
    }
    if (f.fieldtype === 'Link' && f.options) {
      return (
        <div key={f.fieldname} className="space-y-2">
          <Label htmlFor={f.fieldname}>{f.label}</Label>
          <LinkInput
            value={v}
            onChange={(val) => setDraft({ ...draft, [f.fieldname]: val })}
            linkDoctype={f.options}
            placeholder={`Search ${f.options}`}
          />
        </div>
      )
    }
    // Default text input
    return (
      <div key={f.fieldname} className="space-y-2">
        <Label htmlFor={f.fieldname}>{f.label}</Label>
        <Input id={f.fieldname} value={v} onChange={(e) => setDraft({ ...draft, [f.fieldname]: e.target.value })} />
      </div>
    )
  }

  const handleCellChange = (idx: number, fieldname: string, val: any) => {
    const rows = [...(value || [])]
    rows[idx] = { ...(rows[idx] || {}), [fieldname]: val }
    onChange(rows)
  }

  const addRow = () => {
    const next = [...(value || []), {}]
    onChange(next)
    // open editor for the newly added row
    openEditor(next.length - 1)
  }

  const removeRow = (idx: number) => {
    const rows = [...(value || [])]
    rows.splice(idx, 1)
    onChange(rows)
  }

  return (
    <div className="space-y-2">
      <div className="rounded-md border">
        <div className="grid grid-cols-[40px_repeat(auto,1fr)_64px] gap-2 p-2">
          <div className="text-xs font-medium text-muted-foreground">#</div>
          {shown.map((f) => (
            <div key={f.fieldname} className="text-xs font-medium text-muted-foreground">{f.label}</div>
          ))}
          <div className="text-xs font-medium text-muted-foreground">Actions</div>
        </div>
        {fields.length === 0 && (
          <div className="p-3 text-sm text-muted-foreground">No metadata found for child doctype "{childDoctype}". Verify boot configuration.</div>
        )}
        {(!value || value.length === 0) && fields.length > 0 && (
          <div className="p-3 text-sm text-muted-foreground">No rows. Click Add to insert one.</div>
        )}
        {value?.map((row, idx) => (
          <div
            key={idx}
            className="grid items-center gap-2 p-2 cursor-pointer hover:bg-accent/40"
            style={{ gridTemplateColumns: `40px repeat(${shown.length}, minmax(0,1fr)) 64px` }}
            onClick={() => openEditor(idx)}
          >
            <div className="text-xs text-muted-foreground">{idx + 1}</div>
            {shown.map((f) => {
              const v = row[f.fieldname] ?? ''
              if (f.fieldtype === 'Date') {
                return (
                  <Input key={f.fieldname} type="date" value={v} onChange={(e) => handleCellChange(idx, f.fieldname, e.target.value)} />
                )
              }
              if (f.fieldtype === 'Int' || f.fieldtype === 'Float' || f.fieldtype === 'Currency') {
                return (
                  <Input key={f.fieldname} type="number" value={v} onChange={(e) => handleCellChange(idx, f.fieldname, e.target.value)} />
                )
              }
              if (f.fieldtype === 'Select') {
                const opts = f.options?.split('\n') || []
                return (
                  <select
                    key={f.fieldname}
                    value={v}
                    onChange={(e) => handleCellChange(idx, f.fieldname, e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="">Select {f.label}</option>
                    {opts.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                )
              }
              if (f.fieldtype === 'Link' && f.options) {
                return (
                  <LinkInput
                    key={f.fieldname}
                    value={v}
                    onChange={(val) => handleCellChange(idx, f.fieldname, val)}
                    linkDoctype={f.options}
                    placeholder={`Search ${f.options}`}
                  />
                )
              }
              return (
                <Input key={f.fieldname} value={v} onChange={(e) => handleCellChange(idx, f.fieldname, e.target.value)} />
              )
            })}
            <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
              <Button type="button" variant="outline" size="sm" onClick={() => removeRow(idx)}>Remove</Button>
            </div>
          </div>
        ))}
      </div>
      <div>
        <Button type="button" size="sm" onClick={addRow}>Add Row</Button>
      </div>

      {/* Modal Editor */}
      {editingIndex !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={closeEditor} />
          <div className="relative z-10 w-full max-w-2xl rounded-md border bg-background p-4 shadow-lg">
            <div className="mb-4">
              <h3 className="text-lg font-semibold">Edit Row {editingIndex + 1}</h3>
              <p className="text-muted-foreground text-sm">Update all fields for this child row.</p>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {fields.map((f) => renderEditorField(f))}
            </div>
            <div className="mt-6 flex items-center justify-between gap-2">
              <Button type="button" variant="destructive" onClick={deleteEditor}>Delete</Button>
              <div className="ml-auto flex items-center gap-2">
                <Button type="button" variant="outline" onClick={closeEditor}>Cancel</Button>
                <Button type="button" onClick={saveEditor}>Save</Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
