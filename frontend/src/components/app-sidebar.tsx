import * as React from "react"
import { Link } from "react-router-dom"
import {
  IconActivity,
  IconBed,
  IconBuilding,
  IconCalendar,
  IconChartBar,
  IconClipboardList,
  IconCreditCard,
  IconDashboard,
  IconHelp,
  IconPill,
  IconSearch,
  IconSettings,
  IconTestPipe,
  IconUserCheck,
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
  SidebarInput,
} from "@/components/ui/sidebar"
import { useAvailableResources } from "@/hooks/useResourceConfig"

const data = {
  user: {
    name: "HMS User",
    email: "user@hospital.com",
    avatar: "/avatars/user.jpg",
  },
  navMain: [
    {
      title: "My Dashboard",
      url: "/hms/dashboard",
      icon: IconDashboard,
    },
    {
      title: "Reception Dashboard",
      url: "/app/workspace/Reception Dashboard",
      icon: IconUserCheck,
    },
    {
      title: "Doctor Dashboard",
      url: "/app/workspace/Doctor Dashboard",
      icon: IconUsers,
    },
    {
      title: "Pharmacist Dashboard",
      url: "/app/workspace/Pharmacist Dashboard",
      icon: IconPill,
    },
    {
      title: "Analytics",
      url: "/app/workspace/Analytics",
      icon: IconChartBar,
    },
    {
      title: "Accounts",
      url: "/app/workspace/Accounts",
      icon: IconCreditCard,
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
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { resources } = useAvailableResources()
  const [navQuery, setNavQuery] = React.useState("")
  
  // Generate HMS resources navigation
  const hmsResources = React.useMemo(() => {
    const iconMap: Record<string, any> = {
      'Patient': IconUsers,
      'Bed': IconBed,
      'Employee': IconUserCheck,
      'Lab Report': IconTestPipe,
      'Lab Report Type': IconTestPipe,
      'Medicine': IconPill,
      'OP Record': IconClipboardList,
      'Patient Visit': IconCalendar,
      'Ward': IconBuilding,
    }

    return resources.map(resource => ({
      name: resource,
      url: `/hms/resources/${resource.toLowerCase().replace(/\s+/g, '-')}`,
      icon: iconMap[resource] || IconActivity,
    }))
  }, [resources])

  const filteredMain = React.useMemo(() => {
    if (!navQuery) return data.navMain
    const q = navQuery.toLowerCase()
    return data.navMain.filter((i) => i.title.toLowerCase().includes(q))
  }, [navQuery])

  const filteredDocs = React.useMemo(() => {
    if (!navQuery) return hmsResources
    const q = navQuery.toLowerCase()
    return hmsResources.filter((i) => i.name.toLowerCase().includes(q))
  }, [navQuery, hmsResources])

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <Link to="/hms">
                <IconActivity className="!size-5" />
                <span className="text-base font-semibold">HMS</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
        <SidebarInput
          value={navQuery}
          onChange={(e) => setNavQuery(e.target.value)}
          placeholder="Search navigation..."
        />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={filteredMain} />
        <NavDocuments items={filteredDocs} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
