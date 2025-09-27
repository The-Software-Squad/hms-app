import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function MedicinePage() {
  return (
    <MainLayout>
      <DynamicResource doctype="Medicine" title="Medicines" />
    </MainLayout>
  )
}
