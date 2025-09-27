import { MainLayout } from "@/components/main-layout"
import TestComponent from "@/components/test-component"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Users, Calendar, TestTube } from "lucide-react"

// Dashboard cards data
const dashboardCards = [
  {
    title: "Total Patients",
    value: "1,234",
    description: "Active patients in system",
    icon: Users,
    trend: "+12% from last month"
  },
  {
    title: "Today's Visits",
    value: "45",
    description: "Patient visits today",
    icon: Calendar,
    trend: "+5% from yesterday"
  },
  {
    title: "Pending Lab Reports",
    value: "23",
    description: "Reports awaiting review",
    icon: TestTube,
    trend: "-8% from last week"
  },
  {
    title: "Active Staff",
    value: "89",
    description: "Staff members on duty",
    icon: Activity,
    trend: "No change"
  }
]

export default function Dashboard() {
  return (
    <MainLayout>
      <TestComponent />
      <div className="px-5 lg:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">HMS Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to the Hospital Management System
          </p>
        </div>
        
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {dashboardCards.map((card) => {
            const IconComponent = card.icon
            return (
              <Card key={card.title} className="transition-shadow hover:shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {card.title}
                  </CardTitle>
                  <IconComponent className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{card.value}</div>
                  <p className="text-xs text-muted-foreground">
                    {card.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {card.trend}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>
        
        <div className="mt-6 grid gap-5 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest patient visits and system updates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">New patient registered</p>
                    <p className="text-xs text-muted-foreground">John Doe - 2 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Lab report completed</p>
                    <p className="text-xs text-muted-foreground">Blood test for Jane Smith - 15 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Appointment scheduled</p>
                    <p className="text-xs text-muted-foreground">Follow-up visit - 1 hour ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Frequently used functions 
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2">
                <a 
                  href="/hms/resources/patient" 
                  className="flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors"
                >
                  <Users className="h-4 w-4" />
                  <span className="text-sm">Manage Patients</span>
                </a>
                <a 
                  href="/hms/resources/patient-visit" 
                  className="flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors"
                >
                  <Calendar className="h-4 w-4" />
                  <span className="text-sm">Schedule Visit</span>
                </a>
                <a 
                  href="/hms/resources/lab-report" 
                  className="flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors"
                >
                  <TestTube className="h-4 w-4" />
                  <span className="text-sm">Lab Reports</span>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
