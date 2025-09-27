import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Activity, Users, Calendar, FileText, Stethoscope, TestTube } from "lucide-react"

export default function HomePage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">HMS Dashboard</h2>
        <div className="flex items-center space-x-2">
          <Button>
            <Activity className="mr-2 h-4 w-4" />
            Overview
          </Button>
        </div>
      </div>
      
      {/* Welcome Section */}
      <div className="grid gap-4 md:grid-cols-1">
        <Card>
          <CardHeader>
            <CardTitle>Welcome to Hospital Management System</CardTitle>
            <CardDescription>
              Manage your hospital operations efficiently with our comprehensive dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div className="flex items-center space-x-3 p-4 border rounded-lg">
                <Stethoscope className="h-8 w-8 text-blue-500" />
                <div>
                  <h3 className="font-semibold">Doctor Dashboards</h3>
                  <p className="text-sm text-muted-foreground">Access specialized dashboards for medical staff</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border rounded-lg">
                <Users className="h-8 w-8 text-green-500" />
                <div>
                  <h3 className="font-semibold">Patient Management</h3>
                  <p className="text-sm text-muted-foreground">Manage patient records and information</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border rounded-lg">
                <Calendar className="h-8 w-8 text-purple-500" />
                <div>
                  <h3 className="font-semibold">Appointments</h3>
                  <p className="text-sm text-muted-foreground">Schedule and manage appointments</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,234</div>
            <p className="text-xs text-muted-foreground">
              +20% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Appointments</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45</div>
            <p className="text-xs text-muted-foreground">
              +5 from yesterday
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Doctors</CardTitle>
            <Stethoscope className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              All departments covered
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lab Tests</CardTitle>
            <TestTube className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">89</div>
            <p className="text-xs text-muted-foreground">
              +12% from last week
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Navigation Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Dashboards</CardTitle>
            <CardDescription>
              Access role-specific dashboards
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              <Button variant="outline" className="justify-start" asChild>
                <a href="/hms/dashboards/doctor">
                  <Stethoscope className="mr-2 h-4 w-4" />
                  Doctor Dashboard
                </a>
              </Button>
              <Button variant="outline" className="justify-start" asChild>
                <a href="/hms/dashboards/nurse">
                  <Users className="mr-2 h-4 w-4" />
                  Nurse Dashboard
                </a>
              </Button>
              <Button variant="outline" className="justify-start" asChild>
                <a href="/hms/dashboards/admin">
                  <Activity className="mr-2 h-4 w-4" />
                  Admin Dashboard
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Resources</CardTitle>
            <CardDescription>
              Manage hospital resources and data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              <Button variant="outline" className="justify-start" asChild>
                <a href="/hms/resources/patient">
                  <Users className="mr-2 h-4 w-4" />
                  Patients
                </a>
              </Button>
              <Button variant="outline" className="justify-start" asChild>
                <a href="/hms/resources/appointment">
                  <Calendar className="mr-2 h-4 w-4" />
                  Appointments
                </a>
              </Button>
              <Button variant="outline" className="justify-start" asChild>
                <a href="/hms/resources/medical-record">
                  <FileText className="mr-2 h-4 w-4" />
                  Medical Records
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
