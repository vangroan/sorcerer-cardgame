import { useDispatch } from "react-redux"

import { AppDispatch } from "../store"

export function send(payload: any) {
  const dispatch = useDispatch<AppDispatch>()
  dispatch({ type: "server", ...payload })
}
