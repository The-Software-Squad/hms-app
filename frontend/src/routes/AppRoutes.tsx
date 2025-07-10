import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from '../pages/Home';
import ProtectedRoute from './ProtectedRoute';
import { useFrappeAuth } from 'frappe-react-sdk';

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
		</Routes>
	);
};

export default AppRoutes;
