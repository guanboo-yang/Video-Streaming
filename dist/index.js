const ws = new WebSocket('ws://localhost:12345')

ws.onopen = () => {
  console.log('Successfully connected to the server')
}

ws.onerror = err => {
  console.log('Error connecting to the server', err)
}
