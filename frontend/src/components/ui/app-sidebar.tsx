import { Calendar, Home, Inbox, Search, Settings } from "lucide-react"

import {
	Sidebar,
	SidebarContent,
	SidebarGroup,
	SidebarGroupContent,
	SidebarGroupLabel,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar"

// Menu items.
const menuGroups = [
	{
		label: "Patient",
		'items': [
			{
				title: "Home",
				url: "#",
				icon: Home,
			},
			{
				title: "Inbox",
				url: "#",
				icon: Inbox,
			},
			{
				title: "Calendar",
				url: "#",
				icon: Calendar,
			},
			{
				title: "Search",
				url: "#",
				icon: Search,
			},
			{
				title: "Settings",
				url: "#",
				icon: Settings,
			},
		]
	}
]

export function AppSidebar() {
	return (
		<Sidebar>
			<SidebarContent>
				{menuGroups.map((group) => (
					<SidebarGroup key={group.label}>
						<SidebarGroupLabel>{group.label}</SidebarGroupLabel>
						<SidebarGroupContent>
							<SidebarMenu>
								{group.items.map((item) => (
									<SidebarMenuItem key={item.title}>
										<SidebarMenuButton asChild>
											<a href={item.url}>
												<item.icon />
												<span>{item.title}</span>
											</a>
										</SidebarMenuButton>
									</SidebarMenuItem>
								))}
							</SidebarMenu>
						</SidebarGroupContent>
					</SidebarGroup>
				))}
			</SidebarContent>
		</Sidebar>
	)
}