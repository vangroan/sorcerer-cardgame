import { createSlice } from "@reduxjs/toolkit"

export interface GameState {
  joinKey?: string
  game?: object
  discard: object
  moves: Array<object>
}

const initialState: GameState = {
  joinKey: undefined,
  game: undefined,
  discard: {},
  moves: [],
}

const gameSlice = createSlice({
  name: "game",
  initialState,
  reducers: {
    gameInit: (state, action) => {
      if (action.payload?.join_key) {
        state.joinKey = action.payload?.join_key
      }
    },
    gameState: (state) => {},
  },
})

export const { gameInit, gameState } = gameSlice.actions
export default gameSlice.reducer
