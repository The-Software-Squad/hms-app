import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useFrappeAuth } from 'frappe-react-sdk';

interface ProtectedRouteProps {
	children: React.ReactElement;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
	const { currentUser, isLoading, isValidating } = useFrappeAuth();
	const navigate = useNavigate();

	if (isLoading || isValidating) {
		return <div>Loading...</div>;
	}

	if (!currentUser) {
		navigate('/login', { replace: true });
	}
	return children;
};

export default ProtectedRoute;
