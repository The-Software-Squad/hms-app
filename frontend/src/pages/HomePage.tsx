import React from 'react';
import { useFrappeAuth } from 'frappe-react-sdk';

const HomePage: React.FC = () => {
	const { currentUser, logout } = useFrappeAuth();

	return (
		<div>
			<h2>Welcome, {currentUser}</h2>
			<button onClick={() => logout()}>Logout</button>
		</div>
	);
};

export default HomePage;
