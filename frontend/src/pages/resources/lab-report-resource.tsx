import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"
import { LinkInput } from "@/components/resource/LinkInput"

interface LabReport {
  name: string
  patient: string
  report_type: string
  prescribed_by: string
  visit_reference: string
  requested_on: string
  received_on: string
  remarks: string
  report_file: string
}


const columns: ColumnDef<LabReport>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Report ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="font-medium">{row.getValue("name")}</div>,
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
    accessorKey: "report_type",
    header: "Report Type",
    cell: ({ row }) => <div>{row.getValue("report_type")}</div>,
  },
  {
    accessorKey: "prescribed_by",
    header: "Prescribed By",
    cell: ({ row }) => <div>{row.getValue("prescribed_by")}</div>,
  },
  {
    accessorKey: "requested_on",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Requested
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("requested_on")}</div>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      const statusColor = status === "Completed" ? "text-green-600" : "text-orange-600"
      return <div className={`font-medium ${statusColor}`}>{status}</div>
    },
  },
]

const LabReportEditForm = ({
  data,
  onClose: _onClose,
  onSave,
}: {
  data: LabReport | null
  onClose: () => void
  onSave: (data: any) => void
}) => {
  const [formData, setFormData] = React.useState<Partial<LabReport>>(
    data || {
      patient: "",
      report_type: "",
      prescribed_by: "",
      visit_reference: "",
      requested_on: "",
      received_on: "",
      remarks: "",
      report_file: "",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit} className="grid gap-4 py-4">
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
        <Label htmlFor="report_type">Report Type</Label>
        <LinkInput
          value={formData.report_type || ""}
          onChange={(val) => setFormData({ ...formData, report_type: val })}
          linkDoctype="Lab Report Type"
          placeholder="Search Report Type"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="prescribed_by">Prescribed By</Label>
        <LinkInput
          value={formData.prescribed_by || ""}
          onChange={(val) => setFormData({ ...formData, prescribed_by: val })}
          linkDoctype="Employee"
          placeholder="Search Prescriber"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="visit_reference">Visit Reference</Label>
        <LinkInput
          value={formData.visit_reference || ""}
          onChange={(val) => setFormData({ ...formData, visit_reference: val })}
          linkDoctype="Patient Visit"
          placeholder="Search Patient Visit"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="requested_on">Requested On</Label>
        <Input
          id="requested_on"
          type="date"
          value={formData.requested_on || ""}
          onChange={(e) => setFormData({ ...formData, requested_on: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="received_on">Received On</Label>
        <Input
          id="received_on"
          type="date"
          value={formData.received_on || ""}
          onChange={(e) => setFormData({ ...formData, received_on: e.target.value })}
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
    </form>
  )
}

// Fields to fetch from Frappe Lab Report doctype
const labReportFields = [
  "name",
  "patient",
  "report_type",
  "prescribed_by",
  "visit_reference",
  "requested_on",
  "received_on",
  "remarks",
  "report_file",
]

const renderEditForm = (data: LabReport | null, onClose: () => void, onSave: (data: any) => void) => (
  <LabReportEditForm data={data} onClose={onClose} onSave={onSave} />
)

export default function LabReportResource() {
  return (
    <BaseResource<LabReport>
      title="Lab Reports"
      doctype="Lab Report"
      fields={labReportFields}
      columns={columns}
      renderEditForm={renderEditForm}
    />
  )
}
