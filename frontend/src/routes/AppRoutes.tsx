import React from 'react';
import { Routes, Route, createBrowserRouter } from 'react-router-dom';
import HomePage from '../pages/Home';
import { useFrappeAuth } from 'frappe-react-sdk';
import ModernDashboard from '@/components/layouts/modern-dashboard';
import PageNotFound from './PageNotFound';
import DoctorDashboard from '@/pages/dashboards/DoctorDashboard';
import LabTechnicianDashboard from '@/pages/dashboards/LabTechnicianDashboard';
import ReceptionistDashboard from '@/pages/dashboards/ReceptionistDashboard';
import AdminDashboard from '@/pages/dashboards/AdminDashboard';
import NurseDashboard from '@/pages/dashboards/NurseDashboard';
import ProtectedRoute from './ProtectedRoute';

export const appRoutes = createBrowserRouter([
	{
		path: '/hms',
		element: <ModernDashboard />,
		children: [
			{
				path: 'my-dashboard',
				element: <><HomePage /></>,
				index: true,
			},
			{
				path: 'doctor-dashboard',
				element: <DoctorDashboard />,
			},
			{
				path: 'lab-technician-dashboard',
				element: <LabTechnicianDashboard />,
			},
			{
				path: 'reception-dashboard',
				element: <ReceptionistDashboard />,
			},
			{
				path: 'admin-dashboard',
				element: <AdminDashboard />,
			},
			{
				path: 'nurse-dashboard',
				element: <NurseDashboard />,
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

	return (
		<Routes>
			{/* Protected route for home */}
			<Route
				path="/hms"
				element={
					// <ProtectedRoute>
						<HomePage />
					// </ProtectedRoute>
				}
			/>

			{/* 404 */}
			<Route
				path="*"
				element={
					<div>
						<h1>404 - Page Not Found</h1>
					</div>
				}
			/>
		</Routes>
	);
};

export default AppRoutes;
