import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { useFrappeAuth } from 'frappe-react-sdk';
import PageNotFound from './PageNotFound';
import Dashboard from '@/pages/dashboard';
import HMSDashboard from '@/pages/dashboard/hms-dashboard';
import DoctorDashboard from '@/pages/dashboards/doctor-dashboard';
import DynamicResource from '@/pages/resources/dynamic-resource';
import { MainLayout } from '@/components/main-layout';

export const appRoutes = createBrowserRouter([
	{
		path: '/hms',
		children: [
			{
				index: true,
				element: <Dashboard />,
			},
			{
				path: 'dashboard',
				element: <MainLayout><HMSDashboard /></MainLayout>,
			},
			{
				path: 'dashboard/doctor',
				element: <DoctorDashboard />,
			},
			{
				path: 'resources/patient',
				element: <MainLayout><DynamicResource doctype="Patient" title="Patients" /></MainLayout>,
			},
			{
				path: 'resources/employee',
				element: <MainLayout><DynamicResource doctype="Employee" title="Employees" /></MainLayout>,
			},
			{
				path: 'resources/patient-visit',
				element: <MainLayout><DynamicResource doctype="Patient Visit" title="Patient Visits" /></MainLayout>,
			},
			{
				path: 'resources/lab-report',
				element: <MainLayout><DynamicResource doctype="Lab Report" title="Lab Reports" /></MainLayout>,
			},
			{
				path: 'resources/bed',
				element: <MainLayout><DynamicResource doctype="Bed" title="Beds" /></MainLayout>,
			},
			{
				path: 'resources/medicine',
				element: <MainLayout><DynamicResource doctype="Medicine" title="Medicines" /></MainLayout>,
			},
			{
				path: 'resources/op-record',
				element: <MainLayout><DynamicResource doctype="OP Record" title="OP Records" /></MainLayout>,
			},
			{
				path: '*',
				element: <PageNotFound />,
			},
		],
	},
	{
		path: '*',
		element: <PageNotFound />,
	}
]);

const AppRoutes: React.FC = () => {
	const { isLoading, isValidating } = useFrappeAuth();

	if (isLoading || isValidating) {
		return <div>Loading...</div>;
	}

	return null; // Router is handled by RouterProvider in App.tsx
};

export default AppRoutes;
