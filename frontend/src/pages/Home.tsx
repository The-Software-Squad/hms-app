import React from 'react';
import { useFrappeAuth } from 'frappe-react-sdk';
import DashboardLayout from '@/components/layouts/dashboard-layout';

const HomePage: React.FC = () => {
	const { currentUser, logout } = useFrappeAuth();
	console.log('Current User:', currentUser);
	return (
		<div>
			<DashboardLayout>
				<h1>Welcome to the Home Page</h1>
				<p>Hello, {currentUser}</p>
				{currentUser && (
					<div>
						<p>Your email: {currentUser}</p>
						<button onClick={logout}>Logout</button>
					</div>
				)}
				<p>This is a protected route. You must be logged in to see this content.</p>
			</DashboardLayout>
		</div>
	);
};

export default HomePage;
