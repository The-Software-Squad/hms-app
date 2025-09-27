import { BrowserRouter as Router, RouterProvider } from 'react-router-dom';
import { Provider } from 'frappe-react-ui'
import './App.css'
import { FrappeProvider } from 'frappe-react-sdk'
import AppRoutes, { appRoutes } from './routes/AppRoutes';
function App() {

	return (
		<div className="App">
			<FrappeProvider
				url={import.meta.env.VITE_FRAPPE_SITE_URL}
				socketPort={import.meta.env.VITE_FRAPPE_SOCKET_PORT || 9000}
			>		
				<Provider>
					<RouterProvider router={appRoutes} />
				</Provider>
			</FrappeProvider>
		</div>
	)
}

export default App
