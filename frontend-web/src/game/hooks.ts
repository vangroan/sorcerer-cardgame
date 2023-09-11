import { useEffect } from "react"

export function useDocumentEvent(event: string, listener: EventListener | EventListenerObject) {
  useEffect(() => {
    document.addEventListener(event, listener)
    return () => document.removeEventListener(event, listener)
  }, [event, listener])
}
