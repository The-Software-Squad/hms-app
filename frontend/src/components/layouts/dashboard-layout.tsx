import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "../ui/app-sidebar"
import { Navigation } from "../ui/navigation"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
	<SidebarProvider>
	  <AppSidebar />
	  <main className="flex flex-col h-screen w-full">
		<Navigation />
		<section className="flex-1 overflow-y-auto px-10 py-6">
			{children}
		</section>
	  </main>
	</SidebarProvider>
  )
}