import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar, Users, Clock, Activity, Stethoscope, FileText } from "lucide-react"

// Mock data for doctor dashboard
const dashboardData = {
  todayAppointments: 12,
  totalPatients: 156,
  pendingReports: 8,
  avgConsultationTime: "25 min",
  upcomingAppointments: [
    { id: 1, patient: "John Doe", time: "09:00 AM", type: "Consultation" },
    { id: 2, patient: "Jane Smith", time: "09:30 AM", type: "Follow-up" },
    { id: 3, patient: "Robert Johnson", time: "10:00 AM", type: "Check-up" },
    { id: 4, patient: "Mary Wilson", time: "10:30 AM", type: "Consultation" },
  ],
  recentPatients: [
    { id: 1, name: "Alice Brown", lastVisit: "2024-01-15", diagnosis: "Hypertension" },
    { id: 2, name: "David Lee", lastVisit: "2024-01-14", diagnosis: "Diabetes" },
    { id: 3, name: "Sarah Davis", lastVisit: "2024-01-13", diagnosis: "Migraine" },
  ]
}

export default function DoctorDashboard() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Doctor Dashboard</h2>
        <div className="flex items-center space-x-2">
          <Button>
            <Calendar className="mr-2 h-4 w-4" />
            Schedule
          </Button>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Appointments</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.todayAppointments}</div>
            <p className="text-xs text-muted-foreground">
              +2 from yesterday
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.totalPatients}</div>
            <p className="text-xs text-muted-foreground">
              +12 this month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Reports</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.pendingReports}</div>
            <p className="text-xs text-muted-foreground">
              -3 from last week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Consultation</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.avgConsultationTime}</div>
            <p className="text-xs text-muted-foreground">
              +2 min from last month
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Main Content Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Upcoming Appointments */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Upcoming Appointments</CardTitle>
            <CardDescription>
              Your schedule for today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData.upcomingAppointments.map((appointment) => (
                <div key={appointment.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div>
                      <p className="font-medium">{appointment.patient}</p>
                      <p className="text-sm text-muted-foreground">{appointment.type}</p>
                    </div>
                  </div>
                  <div className="text-sm font-medium">{appointment.time}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Recent Patients */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Recent Patients</CardTitle>
            <CardDescription>
              Patients you've seen recently
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData.recentPatients.map((patient) => (
                <div key={patient.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                      <Users className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">{patient.name}</p>
                      <p className="text-sm text-muted-foreground">{patient.diagnosis}</p>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">{patient.lastVisit}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="h-20 flex-col">
              <Stethoscope className="h-6 w-6 mb-2" />
              New Consultation
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <FileText className="h-6 w-6 mb-2" />
              Write Prescription
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Activity className="h-6 w-6 mb-2" />
              View Lab Results
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Calendar className="h-6 w-6 mb-2" />
              Schedule Follow-up
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
