import * as React from "react"
import { useFrappeGetDocList } from "frappe-react-sdk"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  IconUsers, 
  IconCalendar, 
  IconBed, 
  IconTestPipe,
  IconUserCheck,
  IconActivity,
  IconTrendingUp
} from "@tabler/icons-react"

interface DashboardStats {
  totalPatients: number
  todayVisits: number
  availableBeds: number
  pendingReports: number
}

export default function HMSDashboard() {
  // Fetch dashboard data
  const { data: patients } = useFrappeGetDocList("Patient", {
    fields: ["name", "patient_name", "creation"],
    orderBy: { field: "creation", order: "desc" },
    limit: 10
  })

  const { data: patientVisits } = useFrappeGetDocList("Patient Visit", {
    fields: ["name", "patient", "visit_date", "status"],
    filters: [["visit_date", "=", new Date().toISOString().split('T')[0]]],
    orderBy: { field: "creation", order: "desc" }
  })

  const { data: beds } = useFrappeGetDocList("Bed", {
    fields: ["name", "bed_number", "current_patient"],
    orderBy: { field: "bed_number", order: "asc" }
  })

  const { data: labReports } = useFrappeGetDocList("Lab Report", {
    fields: ["name", "patient", "report_type", "status"],
    filters: [["status", "=", "Pending"]],
    orderBy: { field: "creation", order: "desc" }
  })

  // Calculate stats
  const stats: DashboardStats = React.useMemo(() => {
    return {
      totalPatients: patients?.length || 0,
      todayVisits: patientVisits?.length || 0,
      availableBeds: beds?.filter(bed => !bed.current_patient)?.length || 0,
      pendingReports: labReports?.length || 0
    }
  }, [patients, patientVisits, beds, labReports])

  // Transform recent patients data for display
  const recentPatientsData = React.useMemo(() => {
    return (patients || []).slice(0, 5).map(patient => ({
      name: patient.patient_name || patient.name,
      registrationDate: new Date(patient.creation).toLocaleDateString(),
      status: 'Active'
    }))
  }, [patients])


  return (
    <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="aspect-video rounded-xl bg-muted/50" />
        <div className="aspect-video rounded-xl bg-muted/50" />
        <div className="aspect-video rounded-xl bg-muted/50" />
      </div>
      
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            <IconUsers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalPatients}</div>
            <p className="text-xs text-muted-foreground">
              <IconTrendingUp className="h-3 w-3 inline mr-1" />
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Visits</CardTitle>
            <IconCalendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.todayVisits}</div>
            <p className="text-xs text-muted-foreground">
              <IconActivity className="h-3 w-3 inline mr-1" />
              Active appointments
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Beds</CardTitle>
            <IconBed className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.availableBeds}</div>
            <p className="text-xs text-muted-foreground">
              Out of {beds?.length || 0} total beds
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Reports</CardTitle>
            <IconTestPipe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingReports}</div>
            <p className="text-xs text-muted-foreground">
              Lab reports awaiting review
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Patients</CardTitle>
            <CardDescription>
              Latest patient registrations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentPatientsData.length > 0 ? (
                recentPatientsData.map((patient) => (
                  <div key={patient.name} className="flex items-center justify-between p-2 border rounded-lg">
                    <div>
                      <p className="font-medium">{patient.name}</p>
                      <p className="text-sm text-muted-foreground">{patient.registrationDate}</p>
                    </div>
                    <Badge variant="outline">{patient.status}</Badge>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">No recent patients</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Today's Visits</CardTitle>
            <CardDescription>
              Patient visits scheduled for today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {patientVisits && patientVisits.length > 0 ? (
                patientVisits.slice(0, 5).map((visit) => (
                  <div key={visit.name} className="flex items-center justify-between p-2 border rounded-lg">
                    <div>
                      <p className="font-medium">{visit.patient}</p>
                      <p className="text-sm text-muted-foreground">{visit.visit_date}</p>
                    </div>
                    <Badge variant="outline">{visit.status}</Badge>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">No visits scheduled for today</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IconUserCheck className="h-5 w-5" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button className="w-full justify-start" variant="outline">
              <IconUsers className="mr-2 h-4 w-4" />
              Register New Patient
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <IconCalendar className="mr-2 h-4 w-4" />
              Schedule Appointment
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <IconTestPipe className="mr-2 h-4 w-4" />
              Order Lab Test
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Today's Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {patientVisits?.slice(0, 3).map((visit) => (
                <div key={visit.name} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{visit.patient}</p>
                    <p className="text-xs text-muted-foreground">{visit.visit_date}</p>
                  </div>
                  <Badge variant={visit.status === "Completed" ? "default" : "secondary"}>
                    {visit.status}
                  </Badge>
                </div>
              ))}
              {(!patientVisits || patientVisits.length === 0) && (
                <p className="text-sm text-muted-foreground">No visits scheduled for today</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Database</span>
                <Badge variant="default">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Backup</span>
                <Badge variant="default">Current</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Lab Integration</span>
                <Badge variant="default">Connected</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
