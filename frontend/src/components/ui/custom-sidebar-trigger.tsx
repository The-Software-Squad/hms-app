import { useSidebar } from "@/components/ui/sidebar"
import { PanelLeftIcon } from "lucide-react"

export function CustomSidebarTrigger() {
	const { toggleSidebar } = useSidebar()

	return <button className="cursor-pointer" onClick={toggleSidebar}>
		<PanelLeftIcon className="h-4 w-4 text-black dark:text-gray-400" />
		<span className="sr-only">Toggle Sidebar</span>
	</button>
}