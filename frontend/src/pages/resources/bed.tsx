import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function BedPage() {
  return (
    <MainLayout>
      <DynamicResource doctype="Bed" title="Beds" />
    </MainLayout>
  )
}
