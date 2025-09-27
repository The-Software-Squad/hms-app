import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function OPRecordPage() {
  return (
    <MainLayout>
      <DynamicResource doctype="OP Record" title="OP Records" />
    </MainLayout>
  )
}
