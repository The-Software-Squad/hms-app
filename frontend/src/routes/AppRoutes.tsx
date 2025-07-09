import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import LoginPage from '../pages/LoginPage';
import ProtectedRoute from './ProtectedRoute';
import { useFrappeAuth } from 'frappe-react-sdk';

const AppRoutes: React.FC = () => {
	const { currentUser, isLoading, isValidating } = useFrappeAuth();

	if (isLoading || isValidating) {
		return <div>Loading...</div>;
	}

	return (
		<Routes>
			{/* Protected route for home */}
			<Route
				path="/"
				element={
					<ProtectedRoute>
						<HomePage />
					</ProtectedRoute>
				}
			/>

			{/* Public login route */}
			<Route
				path="/login"
				element={currentUser ? <Navigate to="/" replace /> : <LoginPage />}
			/>

			{/* Catch-all fallback */}
			<Route
				path="*"
				element={<Navigate to={currentUser ? '/' : '/login'} replace />}
			/>
		</Routes>
	);
};

export default AppRoutes;
