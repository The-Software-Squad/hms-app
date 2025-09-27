import * as React from "react"
import type { ColumnDef, ColumnFiltersState, SortingState, VisibilityState } from "@tanstack/react-table"
import { flexRender, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel, useReactTable } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, X } from "lucide-react"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { 
  useFrappeGetDocList, 
  useFrappeCreateDoc, 
  useFrappeUpdateDoc
} from "frappe-react-sdk"
import { useResourceConfig } from "@/hooks/useResourceConfig"

interface BaseResourceProps<TData> {
  title: string
  doctype: string
  columns: ColumnDef<TData>[]
  fields?: string[]
  filters?: any[]
  onRowClick?: (row: TData) => void
  renderEditForm?: (data: TData | null, onClose: () => void, onSave: (data: any) => void) => React.ReactNode
}

export function BaseResource<TData>({
  title,
  doctype,
  columns,
  fields,
  filters,
  onRowClick,
  renderEditForm,
}: BaseResourceProps<TData>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})
  const [globalFilter, setGlobalFilter] = React.useState("")
  const [selectedField, setSelectedField] = React.useState<string>("all")
  const [searchText, setSearchText] = React.useState("")
  const [isEditSheetOpen, setIsEditSheetOpen] = React.useState(false)
  const [editingData, setEditingData] = React.useState<TData | null>(null)

  // Get dynamic resource configuration
  const { 
    config, 
    permissions, 
    listViewFields, 
    hasAccess
  } = useResourceConfig(doctype)

  // Use dynamic fields or fallback to provided fields
  const fieldsToFetch = fields || listViewFields || ["name"]

  // Build selectable field options from column accessor keys
  const selectableFields = React.useMemo(() => {
    const opts: { id: string; label: string }[] = []
    for (const col of columns) {
      const id = (col as any).accessorKey as string | undefined
      if (id && typeof id === "string") {
        // Simple label from accessor (Title Case)
        const label = id
          .replace(/_/g, " ")
          .replace(/\b\w/g, (m) => m.toUpperCase())
        opts.push({ id, label })
      }
    }
    return opts
  }, [columns])

  // Debounce applying filters based on search text and selected field
  React.useEffect(() => {
    const t = setTimeout(() => {
      if (selectedField === "all") {
        // Use global filter, clear column filters
        setGlobalFilter(searchText)
        if (columnFilters.length) setColumnFilters([])
      } else {
        // Use column filter, clear global filter
        if (searchText) {
          setColumnFilters([{ id: selectedField, value: searchText }])
        } else {
          setColumnFilters([])
        }
        if (globalFilter) setGlobalFilter("")
      }
    }, 300)
    return () => clearTimeout(t)
  }, [searchText, selectedField])

  // Fetch data from Frappe
  const { data, isLoading, mutate } = useFrappeGetDocList(doctype, {
    fields: fieldsToFetch,
    filters: filters,
    orderBy: {
      field: config?.sort_field || "modified",
      order: (config?.sort_order?.toLowerCase() as "asc" | "desc") || "desc"
    }
  })

  // CRUD operations
  const { createDoc } = useFrappeCreateDoc()
  const { updateDoc } = useFrappeUpdateDoc()

  const handleSave = async (formData: any) => {
    try {
      if (editingData && (editingData as any).name) {
        // Update existing document
        await updateDoc(doctype, (editingData as any).name, formData)
      } else {
        // Create new document
        await createDoc(doctype, formData)
      }
      mutate() // Refresh data
      setIsEditSheetOpen(false)
      setEditingData(null)
    } catch (error) {
      console.error("Error saving document:", error)
    }
  }

  const handleRefresh = () => {
    mutate()
  }

  const handleExport = () => {
    if (!data || data.length === 0) return
    
    // Convert data to CSV
    const headers = columns.map(col => {
      if ('header' in col && typeof col.header === 'string') return col.header
      if ('accessorKey' in col) return col.accessorKey as string
      return 'Unknown'
    })
    
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        columns.map(col => {
          const key = ('accessorKey' in col) ? col.accessorKey as string : 'name'
          const value = row[key] || ''
          // Escape commas and quotes in CSV
          return typeof value === 'string' && (value.includes(',') || value.includes('"')) 
            ? `"${value.replace(/"/g, '""')}"` 
            : value
        }).join(',')
      )
    ].join('\n')
    
    // Download CSV file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `${doctype.toLowerCase().replace(/\s+/g, '_')}_export.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleNewRecord = () => {
    setEditingData(null)
    setIsEditSheetOpen(true)
  }

  const handleEditRecord = (row: TData) => {
    setEditingData(row)
    setIsEditSheetOpen(true)
  }

  const handleCloseSheet = () => {
    setIsEditSheetOpen(false)
    setEditingData(null)
  }

  // Check if user has access to this resource
  if (!hasAccess) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">You don't have permission to access this resource.</p>
      </div>
    )
  }

  const table = useReactTable({
    data: data || [],
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: "includesString",
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
    },
  })

  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Select
            value={selectedField}
            onValueChange={(val) => {
              // preserve current visible text when switching modes
              const current = selectedField === "all"
                ? globalFilter
                : (columnFilters.find((f) => f.id === selectedField)?.value as string) || ""
              setSearchText(current)
              setSelectedField(val)
              // clear filters; effect will apply based on searchText
              setGlobalFilter("")
              setColumnFilters([])
            }}
          >
            <SelectTrigger className="h-9 w-[160px]">
              <SelectValue placeholder="All fields" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="all">All fields</SelectItem>
                {selectableFields.map((f) => (
                  <SelectItem key={f.id} value={f.id}>
                    {f.label}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder={`Search ${title.toLowerCase()}...`}
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
              className="max-w-sm pl-9 pr-8 rounded-full bg-secondary/50 border-transparent hover:bg-secondary/70 focus-visible:border-ring"
            />
            {searchText ? (
              <button
                type="button"
                aria-label="Clear search"
                onClick={() => setSearchText("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 inline-flex size-6 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              >
                <X className="size-4" />
              </button>
            ) : null}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={handleExport} variant="outline" disabled={isLoading || !data || data.length === 0}>
            Export CSV
          </Button>
          <Button onClick={handleRefresh} variant="outline" disabled={isLoading}>
            Refresh
          </Button>
          {permissions?.create && (
            <Button onClick={handleNewRecord}>
              New {title.slice(0, -1)}
            </Button>
          )}
        </div>
      </div>
      
      <div className="rounded-md border">
        <Table data-density="compact">
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                  Loading...
                </TableCell>
              </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => { onRowClick?.(row.original as TData); handleEditRecord(row.original) }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>

      {/* Edit Sheet */}
      <Sheet open={isEditSheetOpen} onOpenChange={setIsEditSheetOpen}>
        <SheetContent>
          <SheetHeader className="p-0">
            <div className="sticky top-0 z-10 flex items-start justify-between gap-2 border-b bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
              <div className="space-y-1">
                <SheetTitle>
                  {editingData ? `Edit ${title.slice(0, -1)}` : `New ${title.slice(0, -1)}`}
                </SheetTitle>
                <SheetDescription>
                  {editingData ? `Update the ${title.toLowerCase().slice(0, -1)} details below.` : `Create a new ${title.toLowerCase().slice(0, -1)} by filling out the form below.`}
                </SheetDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button type="button" variant="outline" size="sm" onClick={handleCloseSheet}>
                  Cancel
                </Button>
                <Button type="submit" size="sm" form="resource-edit-form">
                  Save
                </Button>
              </div>
            </div>
          </SheetHeader>
          {renderEditForm && renderEditForm(editingData, handleCloseSheet, handleSave)}
        </SheetContent>
      </Sheet>
    </div>
  )
}
