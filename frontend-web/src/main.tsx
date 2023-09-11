import React from "react"
import ReactDOM from "react-dom/client"
import { Provider } from "react-redux"

import GameView from "./game/components/GameView"
import "./index.css"

import { api, store } from "./store"

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <GameView />
    </Provider>
  </React.StrictMode>,
)
