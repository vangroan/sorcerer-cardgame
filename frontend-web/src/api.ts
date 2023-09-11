import { BehaviorSubject } from "rxjs"
import { webSocket, WebSocketSubject } from "rxjs/webSocket"

import { gameInit } from "./game/reducer"
import { timeInterval } from "rxjs"

export enum WebsocketAction {
  Connect = "WS_CONNECT",
  Disconnect = "WS_DISCONNECT",
}

export type NextCallback = (next: any) => void

export function connect(address: string, next?: NextCallback): WebSocketSubject<unknown> {
  console.log(`websocket connect: ${address}`)
  const subject = webSocket(address)

  subject.subscribe({
    next: (msg) => {
      console.log("websocket next:", msg)
      if (next) {
        next(msg)
      }
    },
    error: (err) => {
      console.log("websocket error:", err)
    },
    complete: () => {
      console.log("websocket complete")
    },
  })

  return subject
}

// connect("ws://localhost:8765")

export function apiMiddleware() {
  console.log("creating API middleware")

  return (store) => {
    console.log("apiMiddleware: (store) => ...")

    const next = (msg?: any) => {
      console.log("msg.kind:", msg)
      switch (msg?.kind) {
        case "init":
          if (msg?.join) {
            console.log("join_key: ", msg.join)
            store.dispatch(gameInit({ joinKey: msg.join }))
          }
          break
        default:
          console.warn("Websocket message is undefined")
      }
      store.dispatch()
    }

    const subject = connect("ws://localhost:8765", next)
    setTimeout(() => {
      const state = store.getState()
      if (!state.game.joinKey) {
        subject.next({ kind: "init" })
      }
    }, 2000)

    return (next) => (action) => {
      if (action?.type === "server") {
        delete action.type
        subject.next(action)
      } else if (action) {
        next(action)
      }
    }
  }
}

export interface CreateApiOptions {
  baseUrl: string
}

export interface Api {
  middleware: any
  connect: () => void
  getSubject: () => WebSocketSubject<unknown> | undefined
  connectSubject: BehaviorSubject<WebSocketSubject<unknown>>
}

export function createApi(options: CreateApiOptions): Api {
  let subject: WebSocketSubject<unknown>
  let connectSubject = new BehaviorSubject<WebSocketSubject<unknown> | null>(null)

  const handler = (msg: any) => {}

  const connect = () => {
    subject = webSocket(options.baseUrl)

    subject.subscribe({
      next: (msg) => {
        console.log("websocket next:", msg)
        handler(msg)
      },
      error: (err) => {
        console.log("websocket error:", err)
      },
      complete: () => {
        console.log("websocket complete")
      },
    })

    connectSubject.next(subject)
  }

  const middleware = (store) => {
    // Redux store is ready...

    return (next) => (action) => {
      console.debug("middleware: ", action)
      // Action has been dispatched...
      if (!action) return // sometimes undefined

      switch (action.type) {
        case WebsocketAction.Connect:
          connect()
          break
        case WebsocketAction.Disconnect:
          if (subject) subject.complete()
          break
        default:
          next(action)
      }
    }
  }

  return {
    middleware,
    connect,
    getSubject: () => subject,
    connectSubject,
  }
}
