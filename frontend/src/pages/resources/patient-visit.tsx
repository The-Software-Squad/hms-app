import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function PatientVisitPage() {
  return (
    <MainLayout>
      <DynamicResource doctype="Patient Visit" title="Patient Visits" />
    </MainLayout>
  )
}
