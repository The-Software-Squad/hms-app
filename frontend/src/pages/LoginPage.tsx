import React from 'react';
import { useFrappeAuth } from 'frappe-react-sdk';

const LoginPage: React.FC = () => {
	const { login, error, isLoading } = useFrappeAuth();

	const handleLogin = () => {
		login({ username: 'your-username', password: 'your-password' });
	};

	return (
		<div>
			<h2>Login Page</h2>
			<button onClick={handleLogin} disabled={isLoading}>
				Login
			</button>
			{error && <p style={{ color: 'red' }}>{error.message}</p>}
		</div>
	);
};

export default LoginPage;
