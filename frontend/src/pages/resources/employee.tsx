import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function EmployeePage() {
  return (
    <MainLayout>
      <DynamicResource doctype="Employee" title="Employees" />
    </MainLayout>
  )
}
