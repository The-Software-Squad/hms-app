import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"
import { LinkInput } from "@/components/resource/LinkInput"

interface PatientVisit {
  name: string
  op_record: string
  patient: string
  visit_date: string
  doctor: string
  status: string
  follow_up: string
  remarks: string
  medication_details: string
  medication_schedule: string
}


const columns: ColumnDef<PatientVisit>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Visit ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="font-medium text-xs">{row.getValue("name")}</div>,
  },
  {
    accessorKey: "patient",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Patient
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("patient")}</div>,
  },
  {
    accessorKey: "visit_date",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Visit Date
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("visit_date")}</div>,
  },
  {
    accessorKey: "doctor",
    header: "Doctor",
    cell: ({ row }) => <div>{row.getValue("doctor")}</div>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      const statusColor =
        status === "Completed" ? "text-green-600" :
          status === "In Progress" ? "text-blue-600" :
            "text-orange-600"
      return <div className={`font-medium ${statusColor}`}>{status}</div>
    },
  },
  {
    accessorKey: "follow_up",
    header: "Follow Up",
    cell: ({ row }) => <div>{row.getValue("follow_up")}</div>,
  },
]

const PatientVisitEditForm = ({
  data,
  onClose: _onClose,
  onSave,
}: {
  data: PatientVisit | null
  onClose: () => void
  onSave: (data: any) => void
}) => {
  const [formData, setFormData] = React.useState<Partial<PatientVisit>>(
    data || {
      op_record: "",
      patient: "",
      visit_date: "",
      doctor: "",
      status: "Waiting",
      follow_up: "",
      remarks: "",
      medication_details: "",
      medication_schedule: "",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit} className="grid gap-4 py-4">
      <div className="space-y-2">
        <Label htmlFor="op_record">OP Record</Label>
        <Input
          id="op_record"
          value={formData.op_record || ""}
          onChange={(e) => setFormData({ ...formData, op_record: e.target.value })}
          placeholder="Enter OP record"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="patient">Patient</Label>
        <LinkInput
          value={formData.patient || ""}
          onChange={(val) => setFormData({ ...formData, patient: val })}
          linkDoctype="Patient"
          placeholder="Search Patient"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="visit_date">Visit Date</Label>
        <Input
          id="visit_date"
          type="date"
          value={formData.visit_date || ""}
          onChange={(e) => setFormData({ ...formData, visit_date: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="doctor">Doctor</Label>
        <LinkInput
          value={formData.doctor || ""}
          onChange={(val) => setFormData({ ...formData, doctor: val })}
          linkDoctype="Employee"
          placeholder="Search Doctor/Employee"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="status">Status</Label>
        <Input
          id="status"
          value={formData.status || ""}
          onChange={(e) => setFormData({ ...formData, status: e.target.value })}
          placeholder="Waiting/Completed/etc."
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="follow_up">Follow Up Date</Label>
        <Input
          id="follow_up"
          type="date"
          value={formData.follow_up || ""}
          onChange={(e) => setFormData({ ...formData, follow_up: e.target.value })}
        />
      </div>
      <div className="space-y-2 col-span-2">
        <Label htmlFor="remarks">Remarks</Label>
        <Input
          id="remarks"
          value={formData.remarks || ""}
          onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
          placeholder="Enter remarks"
        />
      </div>
      <div className="space-y-2 col-span-2">
        <Label htmlFor="medication_details">Medication Details</Label>
        <Input
          id="medication_details"
          value={formData.medication_details || ""}
          onChange={(e) => setFormData({ ...formData, medication_details: e.target.value })}
          placeholder="Enter medication details"
        />
      </div>
    </form>
  )
}

// Fields to fetch from Frappe Patient Visit doctype
const patientVisitFields = [
  "name",
  "op_record",
  "patient",
  "visit_date",
  "doctor",
  "status",
  "follow_up",
  "remarks",
  "medication_details",
  "medication_schedule",
]

export default function PatientVisitResource() {
  return (
    <BaseResource<PatientVisit>
      title="Patient Visits"
      doctype="Patient Visit"
      fields={patientVisitFields}
      columns={columns}
      renderEditForm={(data: PatientVisit | null, onClose: () => void, onSave: (data: any) => void) => (
        <PatientVisitEditForm data={data} onClose={onClose} onSave={onSave} />
      )}
    />
  )
}
