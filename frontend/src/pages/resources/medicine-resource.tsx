import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"

interface Medicine {
  name: string
  label: string
  composition: string
  description: string
}


const columns: ColumnDef<Medicine>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Medicine ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="font-medium">{row.getValue("name")}</div>,
  },
  {
    accessorKey: "label",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Medicine Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("label")}</div>,
  },
  {
    accessorKey: "composition",
    header: "Composition",
    cell: ({ row }) => <div>{row.getValue("composition")}</div>,
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => <div>{row.getValue("description")}</div>,
  },
]

const MedicineEditForm = ({
  data,
  onClose: _onClose,
  onSave,
}: {
  data: Medicine | null
  onClose: () => void
  onSave: (data: any) => void
}) => {
  const [formData, setFormData] = React.useState<Partial<Medicine>>(
    data || {
      label: "",
      composition: "",
      description: "",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit} className="grid gap-4 py-4">
      <div className="space-y-2">
        <Label htmlFor="label">Medicine Name</Label>
        <Input
          id="label"
          value={formData.label || ""}
          onChange={(e) => setFormData({ ...formData, label: e.target.value })}
          placeholder="Enter medicine name"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="composition">Composition</Label>
        <Input
          id="composition"
          value={formData.composition || ""}
          onChange={(e) => setFormData({ ...formData, composition: e.target.value })}
          placeholder="Enter composition"
        />
      </div>
      <div className="space-y-2 col-span-2">
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          value={formData.description || ""}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Enter description"
        />
      </div>
    </form>
  )
}

// Fields to fetch from Frappe Medicine doctype
const medicineFields = [
  "name",
  "label",
  "composition",
  "description",
]

export default function MedicineResource() {
  return (
    <BaseResource<Medicine>
      title="Medicines"
      doctype="Medicine"
      fields={medicineFields}
      columns={columns}
      renderEditForm={(data: Medicine | null, onClose: () => void, onSave: (data: any) => void) => (
        <MedicineEditForm data={data} onClose={onClose} onSave={onSave} />
      )}
    />
  )
}
