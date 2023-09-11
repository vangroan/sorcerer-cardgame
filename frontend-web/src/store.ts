import { combineReducers, configureStore } from "@reduxjs/toolkit"

import { apiMiddleware, createApi } from "./api"

import appReducer from "./app/reducer"
import gameReducer from "./game/reducer"

export function createStore(api: any) {
  const reducer = combineReducers({
    app: appReducer,
    game: gameReducer,
  })

  const store = configureStore({
    reducer,
    middleware: (getDefaultMiddleware) => {
      return getDefaultMiddleware().concat(api)
    },
  })

  return store
}

export const api = createApi({ baseUrl: "ws://localhost:8765" })
export const store = createStore(api.middleware)

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
