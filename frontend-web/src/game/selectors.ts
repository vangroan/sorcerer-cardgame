import { RootState } from "../store"

export const selectJoinKey = (state: RootState): string | null => state?.game?.joinKey ?? null
