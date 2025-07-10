import { BellIcon, SearchIcon } from "lucide-react";
import { CustomSidebarTrigger } from "./custom-sidebar-trigger";
import { SideSheet } from "./side-sheet";
import { SearchCommand } from "./search-command";

export function Navigation() {
	return (
		<nav className="flex items-center justify-between px-7 py-5 border-b">
			<div className="flex items-center space-x-4">
				<CustomSidebarTrigger />
				<div className="">Hospital Name</div>
			</div>
			<div className="flex items-center space-x-4">
				<SearchCommand />
				<SideSheet
					Trigger={<div className="cursor-pointer p-1 rounded h-min hover:bg-gray-100"><BellIcon className="h-4 w-4" /></div>}
					Content={<div>You have 3 new messages.</div>}
					Header={<div>Notifications</div>}
					Title={<div>New Messages</div>}
					Description={<div>You have 3 new messages.</div>}
				/>
			</div>
		</nav>
	);

}