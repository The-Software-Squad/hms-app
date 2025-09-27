import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function PatientPage() {
  return (
    <MainLayout>
      <DynamicResource doctype="Patient" title="Patients" />
    </MainLayout>
  )
}
