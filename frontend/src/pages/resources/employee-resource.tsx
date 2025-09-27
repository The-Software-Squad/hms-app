import * as React from "react"
import { type ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BaseResource } from "@/components/base-resource"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
// import { SheetFooter } from "@/components/ui/sheet"

interface Employee {
  name: string
  employee_name: string
  department: string
  designation: string
  employee_number: string
  date_of_joining: string
  status: string
}

const columns: ColumnDef<Employee>[] = [
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
    accessorKey: "employee_name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div className="capitalize">{row.getValue("employee_name")}</div>,
  },
  {
    accessorKey: "department",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Department
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("department")}</div>,
  },
  {
    accessorKey: "designation",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Designation
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("designation")}</div>,
  },
  {
    accessorKey: "employee_number",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Employee Number
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("employee_number")}</div>,
  },
  {
    accessorKey: "date_of_joining",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Date of Joining
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => <div>{row.getValue("date_of_joining")}</div>,
  },
  {
    accessorKey: "status",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Status
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ row }) => (
      <div className={`capitalize ${row.getValue("status") === "Active" ? "text-green-600" : "text-red-600"}`}>
        {row.getValue("status")}
      </div>
    ),
  },
]

const EmployeeEditForm = ({
  data,
  onClose: _onClose,
  onSave,
}: {
  data: Employee | null
  onClose: () => void
  onSave: (data: any) => void
}) => {
  const [formData, setFormData] = React.useState<Partial<Employee>>(
    data || {
      employee_name: "",
      department: "",
      designation: "",
      employee_number: "",
      date_of_joining: "",
      status: "Active",
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form id="resource-edit-form" onSubmit={handleSubmit} className="grid gap-4 py-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="employee_name" className="text-right">
          Name
        </Label>
        <Input
          id="employee_name"
          value={formData.employee_name}
          onChange={(e) => setFormData({ ...formData, employee_name: e.target.value })}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="department" className="text-right">
          Department
        </Label>
        <Input
          id="department"
          value={formData.department}
          onChange={(e) => setFormData({ ...formData, department: e.target.value })}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="designation" className="text-right">
          Designation
        </Label>
        <Input
          id="designation"
          value={formData.designation}
          onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="employee_number" className="text-right">
          Employee Number
        </Label>
        <Input
          id="employee_number"
          value={formData.employee_number}
          onChange={(e) => setFormData({ ...formData, employee_number: e.target.value })}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="date_of_joining" className="text-right">
          Date of Joining
        </Label>
        <Input
          id="date_of_joining"
          type="date"
          value={formData.date_of_joining}
          onChange={(e) => setFormData({ ...formData, date_of_joining: e.target.value })}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="status" className="text-right">
          Status
        </Label>
        <Input
          id="status"
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value })}
          className="col-span-3"
        />
      </div>
    </form>
  )
}

// Fields to fetch from Frappe Employee doctype
const employeeFields = [
  "name",
  "employee_name",
  "department",
  "designation",
  "employee_number",
  "date_of_joining",
  "status",
]

export default function EmployeeResource() {
  return (
    <BaseResource<Employee>
      title="Employees"
      doctype="Employee"
      fields={employeeFields}
      columns={columns}
      renderEditForm={(data: Employee | null, onClose: () => void, onSave: (data: any) => void) => (
        <EmployeeEditForm data={data} onClose={onClose} onSave={onSave} />
      )}
    />
  )
}
