import {
	CommandDialog,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem,
	CommandList,
} from "@/components/ui/command"
import { SearchIcon } from "lucide-react"
import React from "react"

function SearchCommandTrigger({ onClick }: { onClick: () => void }) {
	return (
		<div onClick={onClick} className="rounded-full background-muted flex items-center bg-[#0000000A] px-4 py-2 ">
			<p className="text-muted-foreground text-xs text-center flex items-center">
				<SearchIcon className="inline h-4 w-4 mr-1" />
				Search
				<kbd className="ml-1 bg-muted text-muted-foreground pointer-events-none inline-flex h-5 items-center gap-1 rounded border px-1.5 font-mono text-[10px] font-medium opacity-100 select-none">
					<span className="text-xs">⌘</span>+ K
				</kbd>
			</p>
		</div>
	)
}

export function SearchCommand() {
	const [open, setOpen] = React.useState(false)
	const toggleSearch = () => {
		setOpen((open) => !open)
	}

	React.useEffect(() => {
		const down = (e: KeyboardEvent) => {
			if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
				e.preventDefault()
				setOpen((open) => !open)
			}
		}
		document.addEventListener("keydown", down)
		return () => document.removeEventListener("keydown", down)
	}, [])

	return (
		<>
			<SearchCommandTrigger onClick={toggleSearch} />
			<CommandDialog open={open} onOpenChange={setOpen}>
				<CommandInput placeholder="Type a command or search..." />
				<CommandList>
					<CommandEmpty>No results found.</CommandEmpty>
					<CommandGroup heading="Suggestions">
						<CommandItem>Calendar</CommandItem>
						<CommandItem>Search Emoji</CommandItem>
						<CommandItem>Calculator</CommandItem>
					</CommandGroup>
				</CommandList>
			</CommandDialog>
		</>
	)
}