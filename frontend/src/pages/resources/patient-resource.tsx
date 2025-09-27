import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"

interface Patient {
  name: string
  patient_name: string
  patient_age: string
  patient_gender: string
  patient_phone_number: string
  patient_email: string
  patient_location: string
  latest_op_expires_on: string
  follow_up: string
}

const columns: ColumnDef<Patient>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="font-medium">{row.getValue("name")}</div>,
  },
  {
    accessorKey: "patient_name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Patient Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="capitalize">{row.getValue("patient_name")}</div>,
  },
  {
    accessorKey: "patient_age",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Age
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("patient_age")}</div>,
  },
  {
    accessorKey: "patient_gender",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Gender
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="capitalize">{row.getValue("patient_gender")}</div>,
  },
  {
    accessorKey: "patient_phone_number",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Phone
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("patient_phone_number")}</div>,
  },
  {
    accessorKey: "patient_email",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Email
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="lowercase">{row.getValue("patient_email")}</div>,
  },
  {
    accessorKey: "patient_location",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Location
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("patient_location")}</div>,
  },
]

const PatientEditForm = ({ 
  data, 
  onClose: _onClose, 
  onSave 
}: { 
  data: Patient | null; 
  onClose: () => void;
  onSave: (data: any) => void;
}) => {
  const [formData, setFormData] = React.useState<Partial<Patient>>(
    data || {
      patient_name: "",
      patient_age: "",
      patient_gender: "",
      patient_phone_number: "",
      patient_email: "",
      patient_location: "",
      latest_op_expires_on: "",
      follow_up: "",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="patient_name">Patient Name</Label>
          <Input
            id="patient_name"
            value={formData.patient_name || ""}
            onChange={(e) => setFormData({ ...formData, patient_name: e.target.value })}
            placeholder="Enter patient name"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="patient_age">Age</Label>
          <Input
            id="patient_age"
            value={formData.patient_age || ""}
            onChange={(e) => setFormData({ ...formData, patient_age: e.target.value })}
            placeholder="Enter age"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="patient_gender">Gender</Label>
          <Input
            id="patient_gender"
            value={formData.patient_gender || ""}
            onChange={(e) => setFormData({ ...formData, patient_gender: e.target.value })}
            placeholder="Male/Female/Other"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="patient_phone_number">Phone Number</Label>
          <Input
            id="patient_phone_number"
            value={formData.patient_phone_number || ""}
            onChange={(e) => setFormData({ ...formData, patient_phone_number: e.target.value })}
            placeholder="Enter phone number"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="patient_email">Email</Label>
          <Input
            id="patient_email"
            type="email"
            value={formData.patient_email || ""}
            onChange={(e) => setFormData({ ...formData, patient_email: e.target.value })}
            placeholder="Enter email address"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="patient_location">Location</Label>
          <Input
            id="patient_location"
            value={formData.patient_location || ""}
            onChange={(e) => setFormData({ ...formData, patient_location: e.target.value })}
            placeholder="Enter location"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="latest_op_expires_on">OP Expiring On</Label>
          <Input
            id="latest_op_expires_on"
            type="date"
            value={formData.latest_op_expires_on || ""}
            onChange={(e) => setFormData({ ...formData, latest_op_expires_on: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="follow_up">Follow Up</Label>
          <Input
            id="follow_up"
            value={formData.follow_up || ""}
            onChange={(e) => setFormData({ ...formData, follow_up: e.target.value })}
            placeholder="Enter follow up notes"
          />
        </div>
      </div>
      {/* Actions moved to the top header in BaseResource */}
    </form>
  )
}

// Fields to fetch from Frappe Patient doctype
const patientFields = [
  "name",
  "patient_name", 
  "patient_age",
  "patient_gender",
  "patient_phone_number",
  "patient_email",
  "patient_location",
  "latest_op_expires_on",
  "follow_up"
]

export default function PatientResource() {
  return (
    <BaseResource<Patient>
      title="Patients"
      doctype="Patient"
      fields={patientFields}
      columns={columns}
      renderEditForm={(data: Patient | null, onClose: () => void, onSave: (data: any) => void) => (
        <PatientEditForm data={data} onClose={onClose} onSave={onSave} />
      )}
    />
  )
}
