import { createSlice } from "@reduxjs/toolkit"

const appSlice = createSlice({
  name: "app",
  initialState: {},
  reducers: {
    hello: (state) => {
      console.log("Hello, app")
    },
  },
})

export const { hello } = appSlice.actions
export default appSlice.reducer
