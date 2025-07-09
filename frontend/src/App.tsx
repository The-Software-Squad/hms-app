import { BrowserRouter as Router } from 'react-router-dom';

import './App.css'
import { FrappeProvider } from 'frappe-react-sdk'
import AppRoutes from './routes/AppRoutes';
function App() {

	return (
		<div className="App">
			<FrappeProvider
				url={import.meta.env.VITE_FRAPPE_SITE_URL}
				socketPort={import.meta.env.VITE_FRAPPE_SOCKET_PORT || 9000}
			>
				<Router>
					<AppRoutes />
				</Router>
			</FrappeProvider>
		</div>
	)
}

export default App
