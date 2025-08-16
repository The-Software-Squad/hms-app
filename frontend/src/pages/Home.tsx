import React from 'react';
import { useFrappeAuth } from 'frappe-react-sdk';
import ModernDashboard from '@/components/layouts/modern-dashboard';
import { SectionCards } from '@/components/section-cards';
import { ChartAreaInteractive } from '@/components/chart-area-interactive';
import { DataTable } from '@/components/data-table';
import data from '@/components/layouts/data.json';

const HomePage: React.FC = () => {
	const { currentUser, logout } = useFrappeAuth();
	console.log('Current User:', currentUser);
	return (
		<div>
			
		<div className="@container/main flex flex-1 flex-col gap-2">
			<div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
				<SectionCards />
				<div className="px-4 lg:px-6">
					<ChartAreaInteractive />
				</div>
				<DataTable data={data} />
			</div>
		</div>
			{/* <DashboardLayout>
				<h1>Welcome to the Home Page</h1>
				<p>Hello, {currentUser}</p>
				{currentUser && (
					<div>
						<p>Your email: {currentUser}</p>
						<button onClick={logout}>Logout</button>
					</div>
				)}
				<p>This is a protected route. You must be logged in to see this content.</p>
			</DashboardLayout> */}
		</div>
	);
};

export default HomePage;
