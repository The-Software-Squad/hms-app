import {
    Button, Input
  } from 'frappe-react-ui'

export default function TestComponent() {
  return (
    <div>
      <h1>Test Component</h1>
      <Input placeholder="Enter name" />
      <Button onClick={() => {}}>Submit</Button>
    </div>
  )
}