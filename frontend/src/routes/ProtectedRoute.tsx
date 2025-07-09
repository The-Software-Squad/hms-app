import React from 'react';
import { Navigate } from 'react-router-dom';
import { useFrappeAuth } from 'frappe-react-sdk';

interface ProtectedRouteProps {
	children: React.ReactElement;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
	const { currentUser, isLoading, isValidating } = useFrappeAuth();

	if (isLoading || isValidating) {
		return <div>Loading...</div>;
	}

	if (!currentUser) {
		return <Navigate to="/login" replace />;
	}

	return children;
};

export default ProtectedRoute;
