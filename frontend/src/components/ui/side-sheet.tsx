import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

export function SideSheet(
	{ Trigger, Content, Header, Title, Description } = {} as any
) {
	return (
		<Sheet>
			<SheetTrigger>{Trigger}</SheetTrigger>
			<SheetContent>
				<SheetHeader>
					<SheetTitle>{Title}</SheetTitle>
					<SheetDescription>
						{Description}
					</SheetDescription>
				</SheetHeader>
			</SheetContent>
		</Sheet>
	)
}