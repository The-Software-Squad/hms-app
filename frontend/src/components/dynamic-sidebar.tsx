import * as React from "react"
import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { 
  LayoutDashboard, 
  Users, 
  UserCheck, 
  Calendar, 
  FileText, 
  Pill, 
  Bed,
  Building2,
  Activity
} from "lucide-react"
import { useAvailableResources } from "@/hooks/useResourceConfig"

// Icon mapping for different doctypes
const doctypeIcons: Record<string, React.ComponentType<any>> = {
  "Patient": Users,
  "Employee": UserCheck,
  "Patient Visit": Calendar,
  "Lab Report": FileText,
  "Medicine": Pill,
  "Bed": Bed,
  "Ward": Building2,
}

interface DynamicSidebarProps {
  className?: string
}

export function DynamicSidebar({ className }: DynamicSidebarProps) {
  const location = useLocation()
  const { resources, isLoading, error } = useAvailableResources()

  const dashboardItems = [
    {
      title: "Overview",
      href: "/",
      icon: LayoutDashboard,
    },
    {
      title: "Doctor Dashboard",
      href: "/dashboard/doctor",
      icon: UserCheck,
    },
  ]

  if (error) {
    return (
      <div className={cn("pb-12", className)}>
        <div className="space-y-4 py-4">
          <div className="px-3 py-2">
            <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
              HMS Dashboard
            </h2>
            <div className="px-4 text-sm text-muted-foreground">
              Error loading resources: {error.message}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn("pb-12", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            HMS Dashboard
          </h2>
          <div className="space-y-1">
            <h3 className="mb-2 px-4 text-sm font-medium tracking-tight text-muted-foreground">
              Dashboards
            </h3>
            {dashboardItems.map((item) => {
              const Icon = item.icon
              return (
                <Button
                  key={item.href}
                  variant={location.pathname === item.href ? "secondary" : "ghost"}
                  className="w-full justify-start"
                  asChild
                >
                  <Link to={item.href}>
                    <Icon className="mr-2 h-4 w-4" />
                    {item.title}
                  </Link>
                </Button>
              )
            })}
          </div>
        </div>
        
        <Separator />
        
        <div className="px-3 py-2">
          <div className="space-y-1">
            <h3 className="mb-2 px-4 text-sm font-medium tracking-tight text-muted-foreground">
              Resources
            </h3>
            {isLoading ? (
              <div className="px-4 text-sm text-muted-foreground">
                Loading resources...
              </div>
            ) : (
              <ScrollArea className="h-[300px]">
                {resources.map((resource) => {
                  const Icon = doctypeIcons[resource.doctype] || FileText
                  const href = `/resources/${resource.doctype.toLowerCase().replace(/\s+/g, '-')}`
                  
                  return (
                    <Button
                      key={resource.doctype}
                      variant={location.pathname === href ? "secondary" : "ghost"}
                      className="w-full justify-start mb-1"
                      asChild
                    >
                      <Link to={href}>
                        <Icon className="mr-2 h-4 w-4" />
                        {resource.label}
                      </Link>
                    </Button>
                  )
                })}
              </ScrollArea>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
