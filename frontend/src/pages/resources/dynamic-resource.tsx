import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"
import { useResourceConfig, type ResourceField } from "@/hooks/useResourceConfig"
import { useFrappeGetDoc } from "frappe-react-sdk"
import { LinkInput } from "@/components/resource/LinkInput"
import { ChildTableEditor } from "@/components/resource/ChildTableEditor"

interface DynamicResourceProps {
  doctype: string
  title?: string
}
 

// Generic form component that renders fields dynamically
const DynamicEditForm = ({ 
  data, 
  onClose: _onClose, 
  onSave,
  fields,
  doctype
}: { 
  data: any | null; 
  onClose: () => void;
  onSave: (data: any) => void;
  fields: ResourceField[];
  doctype: string;
}) => {
  const [formData, setFormData] = React.useState<Record<string, any>>(
    data || {}
  )

  // Fetch complete record data when editing existing record
  const { data: fullRecordData, isLoading: isLoadingRecord } = useFrappeGetDoc(
    doctype,
    data?.name || null,
    {
      // Only fetch if we have a record name (editing existing record)
      enabled: !!data?.name
    }
  )

  React.useEffect(() => {
    if (data?.name && fullRecordData) {
      // For existing records, use the complete fetched data
      const populatedData: Record<string, any> = {}
      fields.forEach(field => {
        populatedData[field.fieldname] = fullRecordData[field.fieldname] || field.default || ''
      })
      setFormData(populatedData)
    } else if (!data?.name) {
      // Initialize form with default values for new records
      const initialData: Record<string, any> = {}
      fields.forEach(field => {
        if (field.fieldname !== 'name') {
          initialData[field.fieldname] = field.default || ''
        }
      })
      setFormData(initialData)
    }
  }, [data, fields, fullRecordData])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Basic validation
    const errors: Record<string, string> = {}
    
    fields.forEach(field => {
      if (field.reqd && !formData[field.fieldname]) {
        errors[field.fieldname] = `${field.label} is required`
      }
      
      // Email validation
      if (field.fieldtype === 'Data' && field.fieldname.toLowerCase().includes('email')) {
        const email = formData[field.fieldname]
        if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          errors[field.fieldname] = 'Please enter a valid email address'
        }
      }
      
      // Phone validation
      if (field.fieldtype === 'Phone' && formData[field.fieldname]) {
        const phone = formData[field.fieldname]
        if (!/^\+?[\d\s\-\(\)]+$/.test(phone)) {
          errors[field.fieldname] = 'Please enter a valid phone number'
        }
      }
    })
    
    if (Object.keys(errors).length > 0) {
      // Show validation errors (you could use a toast library here)
      console.error('Validation errors:', errors)
      return
    }
    
    onSave(formData)
  }

  const handleFieldChange = (fieldname: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldname]: value
    }))
  }

  const renderField = (field: ResourceField) => {
    if (field.fieldname === 'name' && data) {
      // Don't render name field for existing records
      return null
    }

    // Skip hidden fields
    if (field.hidden) {
      return null
    }

    const value = formData[field.fieldname] !== undefined 
      ? formData[field.fieldname] 
      : (field.default || '')

    switch (field.fieldtype) {
      case 'Date':
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              type="date"
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              required={field.reqd}
              readOnly={field.read_only}
            />
          </div>
        )
      
      case 'Select':
        const selectOptions = field.options?.split('\n') || []
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <select
              id={field.fieldname}
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              required={field.reqd}
              disabled={field.read_only}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="">Select {field.label}</option>
              {selectOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )
      
      case 'Link':
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            {field.options ? (
              <LinkInput
                value={value}
                onChange={(val) => handleFieldChange(field.fieldname, val)}
                linkDoctype={field.options}
                placeholder={`Search ${field.options}`}
                disabled={field.read_only}
                required={field.reqd}
              />
            ) : (
              <Input
                id={field.fieldname}
                value={value}
                onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
                placeholder={`Enter ${field.label.toLowerCase()}`}
                required={field.reqd}
                readOnly={field.read_only}
              />
            )}
          </div>
        )
      
      case 'Currency':
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              type="number"
              step="0.01"
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              placeholder={`Enter ${field.label.toLowerCase()}`}
              required={field.reqd}
              readOnly={field.read_only}
            />
          </div>
        )
      
      case 'Phone':
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              type="tel"
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              placeholder={`Enter ${field.label.toLowerCase()}`}
              required={field.reqd}
              readOnly={field.read_only}
            />
          </div>
        )
      
      case 'Int':
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              type="number"
              step="1"
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              placeholder={`Enter ${field.label.toLowerCase()}`}
              required={field.reqd}
              readOnly={field.read_only}
            />
          </div>
        )
      
      case 'Check':
        return (
          <div key={field.fieldname} className="space-y-2">
            <div className="flex items-center space-x-2">
              <input
                id={field.fieldname}
                type="checkbox"
                checked={value === 1 || value === '1' || value === true}
                onChange={(e) => handleFieldChange(field.fieldname, e.target.checked ? 1 : 0)}
                disabled={field.read_only}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor={field.fieldname}>
                {field.label} {field.reqd && <span className="text-red-500">*</span>}
              </Label>
            </div>
          </div>
        )
      
      case 'Autocomplete':
      case 'Small Text':
      case 'Text':
        return (
          <div key={field.fieldname} className="space-y-2 col-span-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              placeholder={`Enter ${field.label.toLowerCase()}`}
              required={field.reqd}
              readOnly={field.read_only}
            />
          </div>
        )
      
      case 'Text Editor':
        return (
          <div key={field.fieldname} className="space-y-2 col-span-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <textarea
              id={field.fieldname}
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              placeholder={`Enter ${field.label.toLowerCase()}`}
              required={field.reqd}
              readOnly={field.read_only}
              rows={4}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
        )
      
      case 'Attach':
      case 'Attach Image':
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              type="file"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  // For now, just store the file name
                  // In a real implementation, you'd upload the file
                  handleFieldChange(field.fieldname, file.name)
                }
              }}
              required={field.reqd}
              disabled={field.read_only}
              accept={field.fieldtype === 'Attach Image' ? 'image/*' : undefined}
            />
            {value && (
              <p className="text-sm text-muted-foreground">Current: {value}</p>
            )}
          </div>
        )
      
      case 'Table':
        return (
          <div key={field.fieldname} className="space-y-2 col-span-2">
            <Label>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            {field.options ? (
              <ChildTableEditor
                value={Array.isArray(value) ? value : []}
                onChange={(rows) => handleFieldChange(field.fieldname, rows)}
                childDoctype={field.options}
                parentField={field.fieldname}
              />
            ) : (
              <div className="text-sm text-muted-foreground">No child doctype specified.</div>
            )}
          </div>
        )
      default:
        return (
          <div key={field.fieldname} className="space-y-2">
            <Label htmlFor={field.fieldname}>
              {field.label} {field.reqd && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.fieldname}
              value={value}
              onChange={(e) => handleFieldChange(field.fieldname, e.target.value)}
              placeholder={`Enter ${field.label.toLowerCase()}`}
              required={field.reqd}
              readOnly={field.read_only}
            />
          </div>
        )
    }
  }

  // Show loading state when fetching complete record data
  if (data?.name && isLoadingRecord) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <span className="ml-2">Loading record data...</span>
      </div>
    )
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit}>
      <div className="grid gap-4 py-4">
        {fields
          .filter(field => !field.hidden && field.fieldname !== 'name')
          .map(field => renderField(field))
          .filter(Boolean)}
        
        {/* Show name field for existing records as read-only */}
        {data && data.name && (
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={data.name}
              readOnly
              className="bg-muted"
            />
          </div>
        )}
      </div>
    </form>
  )
}

export default function DynamicResource({ doctype, title }: DynamicResourceProps) {
  const { config, permissions, listViewFields, hasAccess } = useResourceConfig(doctype)

  // Generate columns dynamically from list_view_fields configuration
  const columns: ColumnDef<any>[] = React.useMemo(() => {
    if (!config?.fields || !config?.list_view_fields) return []

    // Create a map of fieldname to field info for quick lookup
    const fieldMap = config.fields.reduce((map, field) => {
      map[field.fieldname] = field
      return map
    }, {} as Record<string, any>)

    // Generate columns only for list_view_fields
    return config.list_view_fields.map(fieldname => {
      const field = fieldMap[fieldname] || { fieldname, label: fieldname, fieldtype: 'Data' }
      
      return {
        accessorKey: field.fieldname,
        header: ({ column }) => {
          return (
            <Button
              variant="ghost"
              onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
              {field.label}
              <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
          )
        },
        cell: ({ row }) => {
          const value = row.getValue(field.fieldname)
          return <div className={field.fieldname === 'name' ? 'font-medium' : ''}>{value || ''}</div>
        },
      }
    })
  }, [config])

  if (!hasAccess) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">You don't have permission to access {doctype}.</p>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading {doctype} configuration...</p>
      </div>
    )
  }

  const renderEditForm = (data: any | null, onClose: () => void, onSave: (data: any) => void) => (
    <DynamicEditForm 
      data={data} 
      onClose={onClose} 
      onSave={onSave}
      fields={config.fields}
      doctype={doctype}
    />
  )

  return (
    <BaseResource
      title={title || doctype}
      doctype={doctype}
      columns={columns}
      renderEditForm={renderEditForm}
    />
  )
}
