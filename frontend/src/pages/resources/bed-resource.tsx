import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"
import { LinkInput } from "@/components/resource/LinkInput"

interface Bed {
  name: string
  bed_number: string
  ward: string
  current_patient: string
}

const columns: ColumnDef<Bed>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Bed ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="font-medium">{row.getValue("name")}</div>,
  },
  {
    accessorKey: "bed_number",
    header: "Bed Number",
    cell: ({ row }) => <div>{row.getValue("bed_number")}</div>,
  },
  {
    accessorKey: "ward",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Ward
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("ward")}</div>,
  },
  {
    accessorKey: "bed_type",
    header: "Type",
    cell: ({ row }) => <div>{row.getValue("bed_type")}</div>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      const statusColor = 
        status === "Available" ? "text-green-600" :
        status === "Occupied" ? "text-blue-600" :
        "text-orange-600"
      return <div className={`font-medium ${statusColor}`}>{status}</div>
    },
  },
  {
    accessorKey: "current_patient",
    header: "Current Patient",
    cell: ({ row }) => <div>{row.getValue("current_patient") || "None"}</div>,
  },
]

const BedEditForm = ({ 
  data, 
  onClose: _onClose, 
  onSave 
}: { 
  data: Bed | null; 
  onClose: () => void;
  onSave: (data: any) => void;
}) => {
  const [formData, setFormData] = React.useState<Partial<Bed>>(
    data || {
      bed_number: "",
      ward: "",
      current_patient: "",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit} className="grid gap-4 py-4">
      <div className="space-y-2">
        <Label htmlFor="bed_number">Bed Number</Label>
        <Input
          id="bed_number"
          value={formData.bed_number || ""}
          onChange={(e) => setFormData({ ...formData, bed_number: e.target.value })}
          placeholder="Enter bed number"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="ward">Ward</Label>
        <LinkInput
          value={formData.ward || ""}
          onChange={(val) => setFormData({ ...formData, ward: val })}
          linkDoctype="Ward"
          placeholder="Search Ward"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="current_patient">Current Patient</Label>
        <LinkInput
          value={formData.current_patient || ""}
          onChange={(val) => setFormData({ ...formData, current_patient: val })}
          linkDoctype="Patient"
          placeholder="Search Patient (optional)"
        />
      </div>
    </form>
  )
}

// Fields to fetch from Frappe Bed doctype
const bedFields = [
  "name",
  "bed_number",
  "ward",
  "current_patient"
]

export default function BedResource() {
  return (
    <BaseResource<Bed>
      title="Beds"
      doctype="Bed"
      fields={bedFields}
      columns={columns}
      renderEditForm={(data: Bed | null, onClose: () => void, onSave: (data: any) => void) => (
        <BedEditForm data={data} onClose={onClose} onSave={onSave} />
      )}
    />
  )
}
