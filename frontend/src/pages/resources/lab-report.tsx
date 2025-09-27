import { MainLayout } from "@/components/main-layout"
import DynamicResource from "./dynamic-resource"

export default function LabReportPage() {
  return (
    <MainLayout>
      <DynamicResource doctype="Lab Report" title="Lab Reports" />
    </MainLayout>
  )
}
