

import * as React from "react"
import {
	IconCamera,
	IconChartBar,
	IconDashboard,
	IconDatabase,
	IconFileAi,
	IconFileDescription,
	IconFileWord,
	IconFolder,
	IconHelp,
	IconInnerShadowTop,
	IconListDetails,
	IconReport,
	IconSearch,
	IconSettings,
	IconUsers,
} from "@tabler/icons-react"

import { NavDocuments } from "@/components/nav-documents"
import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar"
import { BadgeDollarSign, MicroscopeIcon, PillIcon, RibbonIcon, ShieldUserIcon, Stethoscope, StethoscopeIcon, UserIcon } from "lucide-react"

const data = {
	user: {
		name: "Nani Samireddy",
		email: "nanisamireddy05@gmail.com",
		avatar: "/avatars/shadcn.jpg",
	},
	navMain: [
		{
			title: "My Dashboard",
			url: "/hms/my-dashboard",
			icon: UserIcon,
		},
		{
			title: "Reception",
			url: "/hms/reception-dashboard",
			icon: IconListDetails,
		},
		{
			title: "Doctor",
			url: "/hms/doctor-dashboard",
			icon: StethoscopeIcon,
		},
		{
			title: "Admin",
			url: "/hms/admin-dashboard",
			icon: ShieldUserIcon,
		},
		{
			title: "Nurse",
			url: "/hms/nurse-dashboard",
			icon: RibbonIcon,
		},
		{
			title: "Lab Technician",
			url: "/hms/lab-technician-dashboard",
			icon: MicroscopeIcon,
		},
	],
	navClouds: [
		{
			title: "Capture",
			icon: IconCamera,
			isActive: true,
			url: "#",
			items: [
				{
					title: "Active Proposals",
					url: "#",
				},
				{
					title: "Archived",
					url: "#",
				},
			],
		},
		{
			title: "Proposal",
			icon: IconFileDescription,
			url: "#",
			items: [
				{
					title: "Active Proposals",
					url: "#",
				},
				{
					title: "Archived",
					url: "#",
				},
			],
		},
		{
			title: "Prompts",
			icon: IconFileAi,
			url: "#",
			items: [
				{
					title: "Active Proposals",
					url: "#",
				},
				{
					title: "Archived",
					url: "#",
				},
			],
		},
	],
	navSecondary: [
		{
			title: "Settings",
			url: "#",
			icon: IconSettings,
		},
		{
			title: "Get Help",
			url: "#",
			icon: IconHelp,
		},
		{
			title: "Search",
			url: "#",
			icon: IconSearch,
		},
	],
	documents: [
		{
			name: "Patient",
			url: "/hms/documents/patient",
			icon: IconDatabase,
		},
		{
			name: "Medicine",
			url: "/hms/documents/medicine",
			icon: PillIcon,
		},
		{
			name: "Payments",
			url: "/hms/documents/payments",
			icon: BadgeDollarSign,
		},
	],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
	return (
		<Sidebar collapsible="offcanvas" {...props}>
			<SidebarHeader>
				<SidebarMenu>
					<SidebarMenuItem>
						<SidebarMenuButton
							asChild
							className="data-[slot=sidebar-menu-button]:!p-1.5"
						>
							<a href="#">
								<IconInnerShadowTop className="!size-5" />
								<span className="text-base font-semibold">Sri Vijaya Lakshmi Hospital</span>
							</a>
						</SidebarMenuButton>
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarHeader>
			<SidebarContent>
				<NavMain items={data.navMain} />
				<NavDocuments items={data.documents} />
				<NavSecondary items={data.navSecondary} className="mt-auto" />
			</SidebarContent>
			<SidebarFooter>
				<NavUser user={data.user} />
			</SidebarFooter>
		</Sidebar>
	)
}
